import importlib
from pathlib import Path
from threading import Thread

import httpx


def test_local_account_setup_masks_inputs_and_enforces_origin(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[2] / 'scripts'))
    module = importlib.import_module('account_setup_ui')
    received = []
    def provision(*values):
        received.append(values)
        return 'gtm_session=synthetic-encrypted; HttpOnly; SameSite=strict; Path=/'
    server = module.AccountServer(('127.0.0.1', 0), provision)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with httpx.Client(trust_env=False) as client:
            base = server.origin + '/' + server.nonce + '/'
            response = client.get(base)
            assert response.text.count('type="password"') == 2
            assert 'no-store' in response.headers['cache-control']
            assert client.get(base + 'font').status_code == 200
            fields = {'csrf': server.nonce, 'email': 'synthetic@example.invalid',
                      'chosen_value': 'synthetic-private-choice'}
            assert client.post(base + 'submit', data=fields,
                headers={'Origin': 'https://synthetic.invalid'}).status_code == 403
            assert not received
            response = client.post(base + 'submit', data=fields, headers={'Origin': server.origin})
            assert response.status_code == 200 and response.json()['ok']
            assert 'HttpOnly' in response.headers['set-cookie']
            assert fields['chosen_value'] not in response.text and fields['email'] not in response.text
            assert received == [(fields['email'], fields['chosen_value'])]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
