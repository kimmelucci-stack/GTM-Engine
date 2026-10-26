import json
import time
from uuid import uuid4

import httpx
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from gtm_engine.api import app
from gtm_engine.sessions import COOKIE


def login_input():
    """Synthetic placeholder, never a reusable account or credential."""
    return {'email': 'synthetic@example.invalid', 'password': 'synthetic-only'}


@pytest.fixture
def session_client(monkeypatch):
    monkeypatch.setenv('SESSION_ENCRYPTION_KEY', Fernet.generate_key().decode())
    monkeypatch.setenv('SUPABASE_URL', 'https://synthetic.invalid')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY', 'synthetic')
    monkeypatch.setenv('APP_ORIGIN', 'http://127.0.0.1:5173')
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def mock_auth(monkeypatch, *, invalid=False):
    owner = str(uuid4())
    def handler(request):
        if request.url.path.endswith('/user'):
            return httpx.Response(200, json={'id': owner, 'is_anonymous': False})
        if '/token' in request.url.path:
            return httpx.Response(400 if invalid else 200, json={'access_token': 'synthetic-access',
                'refresh_token': 'synthetic-refresh', 'user': {'id': owner, 'is_anonymous': False}})
        return httpx.Response(204)
    real = httpx.Client
    monkeypatch.setattr(httpx, 'Client', lambda **kwargs: real(
        **kwargs, transport=httpx.MockTransport(handler)))


def test_login_cookie_is_encrypted_httponly_and_never_returns_tokens(session_client, monkeypatch):
    mock_auth(monkeypatch)
    response = session_client.post('/auth/login', json=login_input(),
                                    headers={'Origin': 'http://127.0.0.1:5173'})
    assert response.status_code == 200
    assert response.json() == {'authenticated': True}
    value = response.headers['set-cookie']
    assert 'HttpOnly' in value and 'SameSite=strict' in value
    assert 'synthetic-access' not in value and 'synthetic-refresh' not in value
    assert 'no-store' in response.headers['cache-control']
    assert session_client.get('/auth/session').status_code == 200
    assert session_client.post('/projects', json={}).status_code == 403
    assert session_client.post('/auth/refresh', headers={'Origin': 'http://127.0.0.1:5173'}).status_code == 200
    assert session_client.post('/auth/logout', headers={'Origin': 'http://127.0.0.1:5173'}).status_code == 200
    assert session_client.get('/auth/session').status_code == 401


@pytest.mark.parametrize('origin', [None, 'null', 'https://synthetic.invalid'])
def test_login_rejects_untrusted_origins_before_auth(session_client, monkeypatch, origin):
    monkeypatch.setattr('gtm_engine.sessions.auth_call', lambda *a, **k: pytest.fail('Auth called'))
    response = session_client.post('/auth/login', json=login_input(),
                                   headers={'Origin': origin} if origin else {})
    assert response.status_code == 403


def test_validation_errors_never_echo_private_inputs(session_client):
    value = 'synthetic-sensitive-value'
    response = session_client.post('/auth/login', json={'email': value, 'password': value},
                                   headers={'Origin': 'http://127.0.0.1:5173'})
    assert response.status_code == 422 and value not in response.text


def test_tampered_and_expired_cookies_are_rejected(session_client, monkeypatch):
    session_client.cookies.set(COOKIE, 'synthetic-tampered')
    assert session_client.get('/auth/session').status_code == 401
    from gtm_engine.sessions import MAX_AGE, cipher
    value = cipher().encrypt(json.dumps({'a': 'synthetic', 'r': 'synthetic',
        'created': int(time.time()) - MAX_AGE - 1}).encode()).decode()
    session_client.cookies.set(COOKIE, value)
    assert session_client.get('/auth/session').status_code == 401


def test_invalid_login_is_generic(session_client, monkeypatch):
    mock_auth(monkeypatch, invalid=True)
    response = session_client.post('/auth/login', json=login_input(),
                                   headers={'Origin': 'http://127.0.0.1:5173'})
    assert response.status_code == 401
    assert 'synthetic' not in response.text
