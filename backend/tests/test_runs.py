from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from gtm_engine.api import app
from gtm_engine.auth import verified_owner
from gtm_engine.persistence.database import PersistenceUnavailable
from gtm_engine.persistence.runs import RunError


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    with TestClient(app) as value:
        yield value
    app.dependency_overrides.clear()


def test_run_routes_require_authentication(client):
    identifier = str(uuid4())
    assert client.post('/projects/' + identifier + '/runs', json={}).status_code == 401
    assert client.get('/projects/' + identifier + '/runs').status_code == 401
    assert client.get('/runs/' + identifier).status_code == 401


@pytest.mark.parametrize('change', [
    {'operation': 'provider.billable'}, {'cap_usd': '15.000001'}, {'cap_usd': '0'},
    {'owner_id': str(uuid4())}, {'module_no': 2}, {'request_id': 'invalid'},
    {'cap_usd': '0.0000001'},
])
def test_run_input_cannot_enable_arbitrary_work(client, monkeypatch, change):
    app.dependency_overrides[verified_owner] = uuid4
    monkeypatch.setattr('gtm_engine.api.runs.enqueue', lambda *args: pytest.fail('Persistence called'))
    body = {'request_id': str(uuid4()), 'operation': 'catalog.validate', **change}
    assert client.post('/projects/' + str(uuid4()) + '/runs', json=body).status_code == 422


def test_enqueue_owner_and_idempotent_response(client, monkeypatch):
    owner, project, request, run = uuid4(), uuid4(), uuid4(), uuid4()
    app.dependency_overrides[verified_owner] = lambda: owner
    created = True
    def enqueue(principal, project_id, request_id, operation, cap):
        assert (principal, project_id, request_id, operation, cap) == (
            owner, project, request, 'catalog.validate', Decimal(10))
        return {'id': run, 'status': 'queued'}, created
    monkeypatch.setattr('gtm_engine.api.runs.enqueue', enqueue)
    body = {'request_id': str(request), 'operation': 'catalog.validate'}
    response = client.post('/projects/' + str(project) + '/runs', json=body)
    assert response.status_code == 202
    assert response.json()['execution_kind'] == 'foundation_check'
    assert 'no-store' in response.headers['cache-control']
    created = False
    assert client.post('/projects/' + str(project) + '/runs', json=body).status_code == 200


@pytest.mark.parametrize('error,status', [(RunError('not_found'), 404),
    (RunError('idempotency_conflict'), 409), (PersistenceUnavailable('sensitive detail'), 503)])
def test_enqueue_safe_errors(client, monkeypatch, error, status):
    app.dependency_overrides[verified_owner] = uuid4
    def fail(*args):
        raise error
    monkeypatch.setattr('gtm_engine.api.runs.enqueue', fail)
    response = client.post('/projects/' + str(uuid4()) + '/runs',
        json={'request_id': str(uuid4()), 'operation': 'catalog.validate'})
    assert response.status_code == status
    assert 'sensitive' not in response.text


def test_read_not_found_and_bounded_list(client, monkeypatch):
    app.dependency_overrides[verified_owner] = uuid4
    monkeypatch.setattr('gtm_engine.api.runs.get', lambda *args: None)
    assert client.get('/runs/' + str(uuid4())).status_code == 404
    monkeypatch.setattr('gtm_engine.api.runs.list_runs', lambda *args: [])
    path = '/projects/' + str(uuid4()) + '/runs'
    assert client.get(path + '?limit=101').status_code == 422
    assert client.get(path + '?limit=0').status_code == 422
    assert client.get(path).json() == {'runs': [], 'limit': 20}
    monkeypatch.setattr('gtm_engine.api.runs.list_runs', lambda *args: [
        {'id': str(uuid4()), 'mode': 'foundation:catalog.validate', 'status': 'queued'}])
    assert client.get(path).json()['runs'][0]['execution_kind'] == 'foundation_check'


def test_status_preserves_real_fields_without_fake_progress(client, monkeypatch):
    app.dependency_overrides[verified_owner] = uuid4
    value = {'id': uuid4(), 'mode': 'foundation:catalog.validate', 'status': 'running',
             'started_at': datetime.now(UTC), 'jobs': [{'status': 'running', 'attempt': 1,
                                                     'lease_expired': True}]}
    monkeypatch.setattr('gtm_engine.api.runs.get', lambda *args: value)
    response = client.get('/runs/' + str(value['id']))
    assert response.json()['status'] == 'running'
    assert response.json()['jobs'][0]['lease_expired']
    assert 'progress' not in response.json()
