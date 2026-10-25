import importlib
from pathlib import Path
from threading import Thread
from urllib.parse import urlencode, urlunsplit

import httpx
import pytest


@pytest.fixture
def setup_server(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / "scripts"))
    module = importlib.import_module("database_setup_ui")
    received = []
    def provision(*values):
        received.append(values)
        return 0
    server = module.SetupServer(("127.0.0.1", 0), provision=provision)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server, received
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def test_form_is_local_masked_and_not_cacheable(setup_server):
    server, _ = setup_server
    with httpx.Client(trust_env=False) as client:
        response = client.get(server.origin + "/" + server.nonce + "/")
        assert response.status_code == 200
        assert response.text.count('type="password"') == 4
        assert 'no-store' in response.headers['cache-control']
        assert response.headers['x-frame-options'] == 'DENY'
        assert 'script-src' not in response.text
        assert client.get(server.origin + '/').status_code == 404
        assert client.get(server.origin + '/' + server.nonce + '/',
                          headers={'Host': 'synthetic.invalid'}).status_code == 404


def test_cross_origin_and_missing_csrf_never_reach_provisioner(setup_server):
    server, received = setup_server
    address = server.origin + "/" + server.nonce + "/submit"
    with httpx.Client(trust_env=False) as client:
        assert client.post(address, data={'csrf': server.nonce},
                           headers={'Origin': 'https://synthetic.invalid'}).status_code == 403
        assert client.post(address, data={'csrf': server.nonce},
                           headers={'Origin': server.origin}).status_code == 403
        assert client.post(address, content=b'x' * 32769,
                           headers={'Origin': server.origin}).status_code == 400
    assert received == []


def test_success_does_not_echo_values_and_closes_form(setup_server, capsys):
    server, received = setup_server
    values = {'csrf': server.nonce, 'administrative': 'synthetic-private-connection',
              'auth_url': 'https://synthetic.invalid', 'public_key': 'synthetic-public-key'}
    with httpx.Client(trust_env=False) as client:
        response = client.post(server.origin + '/' + server.nonce + '/submit',
                               content=urlencode(values), headers={
                                   'Origin': server.origin,
                                   'Content-Type': 'application/x-www-form-urlencoded'})
    assert response.status_code == 200
    assert server.completed
    assert len(received) == 1
    assert 'type="password"' not in response.text
    for name in ('administrative', 'auth_url', 'public_key'):
        assert values[name] not in response.text
        assert values[name] not in capsys.readouterr().out


def test_password_is_encoded_without_echo(setup_server):
    server, received = setup_server
    values = {'csrf': server.nonce,
              'administrative': urlunsplit(('postgresql',
                  'synthetic:[YOUR-PASSWORD]@synthetic.invalid', '/postgres', '', '')),
              'auth_url': 'https://synthetic.invalid',
              'public_key': 'synthetic-public-key'}
    values.update({'db_password': 'synthetic:@/?'})
    with httpx.Client(trust_env=False) as client:
        response = client.post(server.origin + '/' + server.nonce + '/submit',
                               content=urlencode(values), headers={
                                   'Origin': server.origin,
                                   'Content-Type': 'application/x-www-form-urlencoded'})
    assert response.status_code == 200
    assert 'synthetic%3A%40%2F%3F@' in received[0][0]
    assert values['db_password'] not in response.text
