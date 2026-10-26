"""Opt-in real Auth -> API -> Postgres -> worker -> Storage, synthetic accounts only."""

import importlib
import json
import os
import secrets
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from gtm_engine.api import app
from gtm_engine.persistence.database import connection
from gtm_engine.persistence.queue import PostgresQueue
from gtm_engine.persistence.storage import BUCKET, PrivateStorage
from gtm_engine.worker import Handler, SafeRetry, handlers, run_once

pytestmark = pytest.mark.skipif(os.environ.get('GTM_RUN_TEST') != '1', reason='Opt-in real Auth/DB run test')


@pytest.fixture(scope='module')
def live():
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
    settings = importlib.import_module('run_backend').local_settings()
    os.environ.update({k: v for k, v in settings.items() if not os.environ.get(k)})
    app.dependency_overrides.clear()
    base = os.environ['SUPABASE_URL'].rstrip('/')
    administrative = {'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY']}
    public = {'apikey': os.environ['SUPABASE_PUBLISHABLE_KEY']}
    tokens, users = [], []
    target = Path('artifacts/private/runs-live/fixture.json')
    assert not target.exists(), 'Use a fresh fixture directory'
    target.parent.mkdir(parents=True, exist_ok=True)
    fixture = {'users': users, 'projects': []}
    def record():
        target.write_text(json.dumps(fixture))  # UUID metadata only, never tokens or passwords.
    with httpx.Client(timeout=20, trust_env=False, follow_redirects=False) as auth_client:
        try:
            for _ in range(2):
                address = 'gtm-synthetic-' + uuid4().hex + '@example.invalid'
                generated_login = secrets.token_urlsafe(32)
                response = auth_client.post(base + '/auth/v1/admin/users', headers=administrative,
                    json={'email': address, 'password': generated_login, 'email_confirm': True})
                if response.status_code not in (200, 201):
                    raise RuntimeError('synthetic_auth_setup_failed')
                users.append(str(UUID(response.json()['id'])))
                record()
                response = auth_client.post(base + '/auth/v1/token?grant_type=password', headers=public,
                                           json={'email': address, 'password': generated_login})
                if response.status_code != 200:
                    raise RuntimeError('synthetic_auth_login_failed')
                tokens.append(response.json()['access_token'])
                generated_login = ''
            with TestClient(app) as client:
                headers = {'Authorization': 'Bearer ' + tokens[0]}
                response = client.post('/projects', headers=headers, json={
                    'title': 'Synthetic authenticated runs', 'offer_brief': {},
                    'product_in_development': True, 'geo': {}})
                assert response.status_code == 201
                fixture['projects'].append(str(UUID(response.json()['id'])))
                record()
            yield {'owner': users[0], 'project': fixture['projects'][0], 'headers': headers,
                   'other_headers': {'Authorization': 'Bearer ' + tokens[1]}}
        finally:
            # Revoke synthetic refresh sessions before later exact-tree DB/user cleanup.
            for token in tokens:
                response = auth_client.post(base + '/auth/v1/logout?scope=global',
                    headers={**public, 'Authorization': 'Bearer ' + token})
                assert response.status_code in (200, 204)
            if fixture['projects']:
                with connection('gtm_worker') as conn:
                    rows = conn.execute('''select storage_key from gtm.artifacts where run_id in
                        (select id from gtm.runs where project_id=%s)''',
                        (UUID(fixture['projects'][0]),)).fetchall()
                if rows:
                    status, _ = PrivateStorage.configured()._request('DELETE', 'object/' + BUCKET,
                        maximum=16384, json={'prefixes': [r['storage_key'] for r in rows]})
                    assert status == 200
            tokens.clear()


def enqueue(client, live, operation='catalog.validate', request=None):
    response = client.post('/projects/' + live['project'] + '/runs', headers=live['headers'],
        json={'request_id': str(request or uuid4()), 'operation': operation, 'cap_usd': '10'})
    assert response.status_code == 202
    return response.json()


def test_authenticated_enqueue_concurrent_duplicate_and_isolation(live):
    request = str(uuid4())
    def post():
        with TestClient(app) as client:
            response = client.post('/projects/' + live['project'] + '/runs', headers=live['headers'],
                json={'request_id': request, 'operation': 'catalog.validate', 'cap_usd': '10'})
            return response.status_code, response.json()
    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(lambda _: post(), range(2)))
    assert sorted(r[0] for r in result) == [200, 202]
    assert result[0][1]['id'] == result[1][1]['id']
    identifier = result[0][1]['id']
    with TestClient(app) as client:
        path = '/projects/' + live['project'] + '/runs'
        assert client.post(path, headers=live['headers'], json={
            'request_id': request, 'operation': 'catalog.validate', 'cap_usd': '11'}).status_code == 409
        assert client.get('/runs/' + identifier, headers=live['other_headers']).status_code == 404
        assert client.get(path, headers=live['other_headers']).status_code == 404
        assert client.post(path, headers=live['other_headers'], json={
            'request_id': str(uuid4()), 'operation': 'catalog.validate'}).status_code == 404
        assert run_once(PostgresQueue(), handlers()) == 'completed'
        row = client.get('/runs/' + identifier, headers=live['headers']).json()
        assert row['status'] == 'completed' and row['jobs'][0]['attempt'] == 1
        assert row['started_at'] and row['completed_at']
        assert 'lease_token' not in row['jobs'][0]
    with connection('gtm_worker') as conn:
        assert conn.execute('select count(*) n from gtm.runs where project_id=%s',
                            (UUID(live['project']),)).fetchone()['n'] == 1
        assert conn.execute('select count(*) n from gtm.budgets where project_id=%s',
                            (UUID(live['project']),)).fetchone()['n'] == 1


def test_run_status_tracks_retry_failure_partial_and_storage(live):
    with TestClient(app) as client:
        queue = PostgresQueue()
        # Exercise terminal outcomes first; leave the explicitly scheduled retry until last.
        partial = enqueue(client, live)
        assert run_once(queue, {'catalog.validate': Handler(lambda job: (_ for _ in ()).throw(
            SafeRetry()), False)}) == 'failed'
        assert client.get('/runs/' + partial['id'], headers=live['headers']).json()['status'] == 'failed'
        limited = enqueue(client, live)
        limited_job = queue.claim(['catalog.validate'])
        assert queue.finish(limited_job, 'partial', 'handler_failed')
        assert client.get('/runs/' + limited['id'], headers=live['headers']).json()['status'] == 'partial'
        archived = enqueue(client, live, 'catalog.archive')
        assert run_once(queue, handlers()) == 'completed'
        row = client.get('/runs/' + archived['id'], headers=live['headers']).json()
        assert row['status'] == 'completed' and len(row['artifact_ids']) == 1
        assert client.get('/artifacts/' + row['artifact_ids'][0] + '/content',
                          headers=live['headers']).status_code == 200
        rows = client.get('/projects/' + live['project'] + '/runs?limit=2',
                          headers=live['headers']).json()
        assert len(rows['runs']) == 2
        run = enqueue(client, live)
        job = queue.claim(['catalog.validate'])
        assert job and str(job.run_id) == run['id']
        path = '/runs/' + run['id']
        assert client.get(path, headers=live['headers']).json()['status'] == 'running'
        assert queue.finish(job, 'queued', 'retry_safe')
        row = client.get(path, headers=live['headers']).json()
        assert row['status'] == 'queued' and row['completed_at'] is None
        assert not queue.finish(job, 'completed')
