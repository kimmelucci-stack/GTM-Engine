"""One-use loopback bootstrap for the owner's application account. Never a public signup API."""

import json
import os
import re
import secrets
from html import escape
from threading import Thread
from urllib.parse import parse_qs

import httpx
from database_setup_ui import CSS, ROOT, SCRIPT
from database_setup_ui import Handler as BaseHandler
from fastapi import Response
from gtm_engine.sessions import auth_call, origin, set_session
from run_backend import local_settings
from storage_setup_ui import StorageServer


def configure(address: str, chosen_value: str) -> str:
    if (not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', address) or len(address) > 320
            or not 12 <= len(chosen_value) <= 1024):
        raise ValueError('invalid_account_input')
    base = os.environ['SUPABASE_URL'].rstrip('/')
    with httpx.Client(timeout=15, trust_env=False, follow_redirects=False) as client:
        response = client.post(base + '/auth/v1/admin/users',
            headers={'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY']},
            json={'email': address, 'password': chosen_value, 'email_confirm': True})
    if response.status_code not in (200, 201):
        raise ValueError('account_setup_failed')
    data = auth_call('token?grant_type=password', payload={'email': address, 'password': chosen_value})
    result = Response()
    set_session(result, data)
    return result.headers['set-cookie']


def page(nonce: str) -> str:
    script = SCRIPT.replace('form.hidden = true;',
                            'form.hidden = true; window.location.assign(' + json.dumps(origin()) + ');')
    return f"""<!doctype html><html lang="it"><meta charset="utf-8">
    <title>Il tuo accesso · GTM Engine</title><style>{CSS}</style><header>GTM Engine</header>
    <main><h1>Crea il tuo accesso</h1><p>Scegli le credenziali per entrare nel tuo spazio di lavoro.
    Sono separate dall’accesso al pannello Supabase.</p>
    <div id="setup-status" class="message" hidden role="status"></div>
    <form action="submit" method="post" autocomplete="off">
    <input type="hidden" name="csrf" value="{escape(nonce)}">
    <label for="account-email">Email</label><input id="account-email" name="email" type="password"
      autocomplete="off" required maxlength="320" spellcheck="false">
    <label for="account-pass">Scegli una password</label><input id="account-pass" name="chosen_value"
      type="password" required minlength="12" maxlength="1024" autocomplete="new-password">
    <small>Almeno 12 caratteri. Non usare la password del database.</small>
    <button type="submit">Crea il mio accesso</button></form>
    <p class="note">Modulo locale monouso. Nessun valore viene scritto in chat, nei log o nei file.
    La password viene affidata al servizio di autenticazione. Al termine entrerai nell’applicazione.</p>
    </main><script nonce="{escape(nonce)}">{script}</script></html>"""


class AccountServer(StorageServer):
    def __init__(self, address, provision=configure):
        super().__init__(address, provision)
        self.RequestHandlerClass = Handler
        self.cookie = ''


class Handler(BaseHandler):
    server: AccountServer

    def end_headers(self) -> None:
        if self.server.cookie:
            self.send_header('Set-Cookie', self.server.cookie)
        super().end_headers()

    def do_GET(self) -> None:
        prefix = '/' + self.server.nonce + '/'
        if not self.allowed_host() or self.path not in {prefix, prefix + 'font'}:
            self.respond(404, b'Not found', 'text/plain')
            return
        if self.path.endswith('/font'):
            self.respond(200, (ROOT / 'frontend/public/fonts/InterVariable.woff2').read_bytes(),
                         'font/woff2')
            return
        self.respond(200, page(self.server.nonce).encode())

    def do_POST(self) -> None:
        if (not self.allowed_host() or self.path != '/' + self.server.nonce + '/submit'
                or self.headers.get('Origin') != self.server.origin or self.server.completed):
            self.reject_post(403, b'Forbidden')
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if (not 0 < size <= 8192 or self.headers.get('Content-Type', '').split(';')[0]
                    != 'application/x-www-form-urlencoded'):
                self.reject_post(400, b'Invalid request')
                return
            fields = parse_qs(self.rfile.read(size).decode(), max_num_fields=3, strict_parsing=True)
            if (set(fields) != {'csrf', 'email', 'chosen_value'}
                    or any(len(v) != 1 for v in fields.values())
                    or not secrets.compare_digest(fields['csrf'][0], self.server.nonce)):
                self.respond(403, b'Forbidden', 'text/plain')
                return
            self.server.cookie = self.server.provision(fields['email'][0].strip(), fields['chosen_value'][0])
            self.server.completed = True
        except Exception:  # noqa: BLE001 -- never echo Auth response or submitted values
            self.server.completed = False
        message = ('Accesso creato. Apertura del tuo spazio di lavoro…' if self.server.completed else
                   'Accesso non creato. Controlla email e password; se hai già un account, usa Accedi nell’app.')
        self.respond(200 if self.server.completed else 400,
                     json.dumps({'ok': self.server.completed, 'message': message}).encode(),
                     'application/json')
        if self.server.completed:
            Thread(target=self.server.shutdown, daemon=True).start()


if __name__ == '__main__':
    os.environ.update(local_settings())
    with AccountServer(('127.0.0.1', 0)) as server:
        print(server.origin + '/' + server.nonce + '/', flush=True)
        server.serve_forever()
