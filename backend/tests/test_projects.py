from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from gtm_engine import auth
from gtm_engine.api import app
from gtm_engine.persistence.database import PersistenceUnavailable, connection


@pytest.fixture(autouse=True)
def clean_overrides():
    yield
    app.dependency_overrides.clear()


def test_project_requires_authentication():
    with TestClient(app) as client:
        assert client.get('/projects/' + str(uuid4())).status_code == 401
        assert client.post('/projects', json={}).status_code == 401


def test_other_owner_and_missing_project_share_404(monkeypatch):
    owner = uuid4()
    app.dependency_overrides[auth.verified_owner] = lambda: owner
    seen = []
    def lookup(principal, project):
        seen.append(principal)
    monkeypatch.setattr('gtm_engine.api.projects.get_project', lookup)
    with TestClient(app) as client:
        assert client.get('/projects/' + str(uuid4())).status_code == 404
    assert seen == [owner]


def test_owner_cannot_be_supplied_in_body_and_errors_are_redacted(monkeypatch):
    app.dependency_overrides[auth.verified_owner] = lambda: uuid4()
    values = {'title': 'Synthetic', 'offer_brief': {}, 'product_in_development': False, 'geo': {}}
    def unavailable(*args):
        raise PersistenceUnavailable('synthetic sensitive connection detail')
    monkeypatch.setattr('gtm_engine.api.projects.create_project', unavailable)
    with TestClient(app) as client:
        assert client.post('/projects', json={**values, 'owner_id': str(uuid4())}).status_code == 422
        result = client.post('/projects', json=values)
    assert result.status_code == 503
    assert 'sensitive' not in result.text


def test_database_missing_configuration_fails_closed(monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    with (pytest.raises(PersistenceUnavailable, match='database_not_configured'),
          connection('gtm_api', uuid4())):
        pytest.fail('Unexpected connection')


def test_project_roundtrip_response_and_principal(monkeypatch):
    owner = uuid4()
    app.dependency_overrides[auth.verified_owner] = lambda: owner
    values = {'title': 'Synthetic', 'offer_brief': {'offer': 'synthetic'},
              'product_in_development': False, 'geo': {'country': 'IT'}}
    result = {**values, 'locale': 'it-IT', 'id': uuid4(), 'created_at': datetime.now(UTC)}
    def create(principal, payload):
        assert principal == owner
        assert 'owner_id' not in payload
        return result
    monkeypatch.setattr('gtm_engine.api.projects.create_project', create)
    monkeypatch.setattr('gtm_engine.api.projects.get_project', lambda *args: result)
    with TestClient(app) as client:
        created = client.post('/projects', json=values)
        assert created.status_code == 201
        fetched = client.get('/projects/' + str(result['id']))
        assert fetched.status_code == 200
        assert fetched.json() == created.json()
        assert 'owner_id' not in fetched.json()


@pytest.mark.parametrize('status,payload,expected', [
    (401, {}, 401), (500, {}, 503), (200, {'id': str(uuid4()), 'is_anonymous': True}, 401),
    (200, {'id': 'invalid', 'is_anonymous': False}, 503), (200, {}, 401),
])
def test_auth_fails_closed(monkeypatch, status, payload, expected):
    monkeypatch.setenv('SUPABASE_URL','https://synthetic.invalid')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','synthetic-public-key')
    real_client = httpx.Client
    monkeypatch.setattr(auth.httpx,'Client',lambda **kwargs: real_client(
        transport=httpx.MockTransport(lambda req: httpx.Response(status,json=payload)), **kwargs))
    with pytest.raises(HTTPException) as error:
        auth.verified_owner(HTTPAuthorizationCredentials(scheme='Bearer',credentials='synthetic'))
    assert error.value.status_code == expected


def test_auth_uses_verified_user_id(monkeypatch):
    owner = uuid4()
    monkeypatch.setenv('SUPABASE_URL','https://synthetic.invalid')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY','synthetic-public-key')
    real_client = httpx.Client
    monkeypatch.setattr(auth.httpx,'Client',lambda **kwargs: real_client(
        transport=httpx.MockTransport(lambda req: httpx.Response(
            200,json={'id': str(owner),'is_anonymous': False})), **kwargs))
    assert auth.verified_owner(HTTPAuthorizationCredentials(
        scheme='Bearer',credentials='synthetic')) == owner
