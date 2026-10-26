"""Opt-in real browser/Auth/API/DB/worker test with transient synthetic accounts."""

import importlib
import json
import os
import secrets
import sys
from pathlib import Path
from threading import Thread
from uuid import UUID, uuid4

import httpx
import pytest

from gtm_engine.persistence.database import connection
from gtm_engine.persistence.storage import BUCKET, PrivateStorage

pytestmark = pytest.mark.skipif(os.environ.get('GTM_APP_TEST') != '1', reason='Opt-in real application browser test')


def test_real_private_workspace():
    from playwright.sync_api import expect, sync_playwright
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
    os.environ.update(importlib.import_module('run_backend').local_settings())
    folder = Path('artifacts/private/application-live')
    folder.mkdir(parents=True, exist_ok=True)
    metadata_path = folder / 'fixture.json'
    assert not metadata_path.exists(), 'Use a new synthetic fixture'
    metadata = {'users': [], 'projects': []}
    base = os.environ['SUPABASE_URL'].rstrip('/')
    server_headers = {'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY']}
    accounts = []
    with httpx.Client(timeout=20, trust_env=False, follow_redirects=False) as admin:
        for _ in range(2):
            address, generated_login = 'gtm-ui-' + uuid4().hex + '@example.invalid', secrets.token_urlsafe(32)
            response = admin.post(base + '/auth/v1/admin/users', headers=server_headers,
                json={'email': address, 'password': generated_login, 'email_confirm': True})
            if response.status_code not in (200, 201):
                raise RuntimeError('synthetic_account_setup_failed')
            metadata['users'].append(str(UUID(response.json()['id'])))
            metadata_path.write_text(json.dumps(metadata))
            accounts.append((address, generated_login))
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel=os.environ.get('GTM_BROWSER_CHANNEL', 'chrome'))
            try:
                context = browser.new_context(viewport={'width': 1440, 'height': 1000})
                page = context.new_page()
                errors, external = [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda request: external.append(request.url)
                        if not request.url.startswith('http://127.0.0.1:5173/') else None)
                page.goto('http://127.0.0.1:5173/')
                expect(page.get_by_role('heading', name='Accedi a GTM Engine')).to_be_visible(timeout=15000)
                page.screenshot(path=str(folder / 'login-desktop.png'))
                page.get_by_label('Email', exact=True).fill(accounts[0][0])
                page.get_by_label('Password', exact=True).fill(accounts[0][1])
                page.get_by_role('button', name='Accedi', exact=True).click()
                expect(page.get_by_role('heading', name='Il tuo primo progetto')).to_be_visible(timeout=15000)
                cookies = context.cookies()
                assert any(c['name'] == 'gtm_session' and c['httpOnly'] for c in cookies)
                assert page.evaluate('document.cookie') == ''
                assert page.evaluate('localStorage.length + sessionStorage.length') == 0
                page.get_by_role('button', name='Nuovo progetto', exact=True).click()
                page.get_by_label('Nome progetto', exact=True).fill('Progetto di prova')
                page.get_by_label('Prodotto o servizio', exact=True).fill('Offerta sintetica per una verifica tecnica.')
                page.get_by_label('Mercato di riferimento', exact=True).fill('Torino, Piemonte, Italia')
                page.get_by_label('Il prodotto o servizio è ancora in sviluppo').check()
                page.get_by_role('dialog').get_by_role('button', name='Crea progetto', exact=True).click()
                expect(page.get_by_role('heading', name='Progetto di prova', exact=True)).to_be_visible(timeout=15000)
                with connection('gtm_api', UUID(metadata['users'][0])) as conn:
                    rows = conn.execute('select id from gtm.projects where owner_id=%s',
                                        (UUID(metadata['users'][0]),)).fetchall()
                metadata['projects'] = [str(r['id']) for r in rows]
                metadata_path.write_text(json.dumps(metadata))
                assert len(rows) == 1
                page.get_by_role('button', name='Verifica spazio di lavoro', exact=True).click()
                expect(page.get_by_text('Completata', exact=True)).to_be_visible(timeout=45000)
                expect(page.get_by_role('button', name='Scarica evidenza', exact=True)).to_be_visible()
                page.get_by_role('button', name='Dettagli', exact=True).click()
                expect(page.get_by_text('Tentativo 1', exact=False)).to_be_visible()
                page.get_by_role('button', name='Nascondi dettagli', exact=True).click()
                with page.expect_download() as download:
                    page.get_by_role('button', name='Scarica evidenza', exact=True).click()
                download.value.save_as(folder / 'evidenza.json')
                assert json.loads((folder / 'evidenza.json').read_text())['job_title_count'] > 0
                assert page.locator('button svg[data-icon="arrow"], button svg[data-icon="chevron"]').count() == 0
                assert page.locator('button').filter(has_text='→').count() == 0
                assert page.evaluate("getComputedStyle(document.body).fontFamily").startswith('Inter')
                page.screenshot(path=str(folder / 'project-desktop.png'))
                page.reload()
                expect(page.get_by_role('heading', name='Progetti', exact=True)).to_be_visible(timeout=15000)
                page.get_by_role('button').filter(has_text='Progetto di prova').click()
                expect(page.get_by_role('button', name='Scarica evidenza', exact=True)).to_be_visible(timeout=15000)
                page.set_viewport_size({'width': 390, 'height': 844})
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
                page.screenshot(path=str(folder / 'project-mobile.png'), full_page=True)
                page.get_by_role('button', name='Esci', exact=True).click()
                expect(page.get_by_role('heading', name='Accedi a GTM Engine')).to_be_visible(timeout=15000)
                page.get_by_label('Email', exact=True).fill(accounts[1][0])
                page.get_by_label('Password', exact=True).fill(accounts[1][1])
                page.get_by_role('button', name='Accedi', exact=True).click()
                expect(page.get_by_role('heading', name='Il tuo primo progetto')).to_be_visible(timeout=15000)
                assert page.get_by_text('Progetto di prova', exact=True).count() == 0
                page.get_by_role('button', name='Esci', exact=True).click()
                expect(page.get_by_role('heading', name='Accedi a GTM Engine')).to_be_visible(timeout=15000)
                assert not errors and not external
            finally:
                context.request.post('http://127.0.0.1:5173/api/auth/logout',
                                     headers={'Origin': 'http://127.0.0.1:5173'})
                browser.close()
                accounts.clear()
        # The test's application logout revoked both sessions. Remove only its Storage objects.
        if metadata['projects']:
            with connection('gtm_worker') as conn:
                rows = conn.execute('''select storage_key from gtm.artifacts where run_id in
                    (select id from gtm.runs where project_id=any(%s))''',
                    ([UUID(p) for p in metadata['projects']],)).fetchall()
            if rows:
                status, _ = PrivateStorage.configured()._request('DELETE', 'object/' + BUCKET,
                    maximum=16384, json={'prefixes': [r['storage_key'] for r in rows]})
                assert status == 200


def test_first_account_bootstrap_real_cookie_handoff():
    from playwright.sync_api import expect, sync_playwright
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
    os.environ.update(importlib.import_module('run_backend').local_settings())
    setup = importlib.import_module('account_setup_ui')
    from gtm_engine.sessions import cipher
    folder = Path('artifacts/private/application-live')
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / 'bootstrap-fixture.json'
    assert not target.exists(), 'Use a new synthetic bootstrap fixture'
    address = 'gtm-bootstrap-' + uuid4().hex + '@example.invalid'
    chosen_value = secrets.token_urlsafe(32)
    server = setup.AccountServer(('127.0.0.1', 0))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel=os.environ.get('GTM_BROWSER_CHANNEL', 'chrome'))
            context = browser.new_context()
            try:
                page = context.new_page()
                page.goto(server.origin + '/' + server.nonce + '/')
                page.get_by_label('Email', exact=True).fill(address)
                page.get_by_label('Scegli una password', exact=True).fill(chosen_value)
                page.get_by_role('button', name='Crea il mio accesso', exact=True).click()
                expect(page.get_by_role('heading', name='Il tuo primo progetto')).to_be_visible(timeout=20000)
                encrypted = next(c['value'] for c in context.cookies() if c['name'] == 'gtm_session')
                # Only this server-side test process has the key; page JavaScript cannot read it.
                session = json.loads(cipher().decrypt(encrypted.encode()))
                with httpx.Client(timeout=15, trust_env=False) as client:
                    response = client.get(os.environ['SUPABASE_URL'].rstrip('/') + '/auth/v1/user',
                        headers={'apikey': os.environ['SUPABASE_PUBLISHABLE_KEY'],
                                 'Authorization': 'Bearer ' + session['a']})
                assert response.status_code == 200
                target.write_text(json.dumps({'users': [str(UUID(response.json()['id']))], 'projects': []}))
                session.clear()
                assert page.evaluate('document.cookie') == ''
                page.get_by_role('button', name='Esci', exact=True).click()
                expect(page.get_by_role('heading', name='Accedi a GTM Engine')).to_be_visible()
                assert server.completed
            finally:
                context.request.post('http://127.0.0.1:5173/api/auth/logout',
                                     headers={'Origin': 'http://127.0.0.1:5173'})
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
