"""Opt-in browser acceptance; requires frontend on localhost:5173."""

import os
from pathlib import Path

import pytest


@pytest.mark.skipif(os.environ.get("GTM_UI_TEST") != "1", reason="Opt-in frontend browser test")
def test_review_selection_guard_and_manual_pending():
    from playwright.sync_api import sync_playwright

    artifacts = Path("artifacts/private/review-ui")
    artifacts.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel=os.environ.get('GTM_BROWSER_CHANNEL'))
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        posts = []
        external_requests = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: posts.append(request.url)
                if request.method == "POST" else None)
        page.on("request", lambda request: external_requests.append(request.url)
                if not request.url.startswith("http://127.0.0.1:5173/") else None)
        page.goto("http://127.0.0.1:5173/demo")
        assert page.evaluate("""async () => {
            await document.fonts.load('13px Inter');
            return [...document.fonts].some(f => f.family === 'Inter' && f.status === 'loaded');
        }""")
        assert page.evaluate("getComputedStyle(document.body).fontFamily").startswith('Inter')
        assert page.locator('button svg[data-icon="arrow"], button svg[data-icon="chevron"], '
                            'button svg[data-icon="external"]').count() == 0
        assert not page.get_by_role("button").filter(has_text="→").count()
        confirm = page.get_by_role("button", name="Conferma selezione di prova")
        assert confirm.is_enabled()
        first = page.get_by_role("checkbox", name="Includi Atlas Club", exact=True)
        first.uncheck()
        assert confirm.is_disabled()
        page.get_by_role("checkbox", name="Includi Campo Collective", exact=True).check()
        assert confirm.is_enabled()
        page.get_by_role("checkbox", name="Includi Spazio Uno", exact=True).check()
        assert confirm.is_disabled()
        page.get_by_role("checkbox", name="Includi Spazio Uno", exact=True).uncheck()
        page.evaluate("window.scrollTo(0,0)")
        page.screenshot(path=str(artifacts / "desktop.png"), full_page=True)
        page.get_by_role("button", name="Direzione di design", exact=True).click()
        assert page.get_by_role("link", name="Interfaccia Attio", exact=True).is_visible()
        page.get_by_role("button", name="Chiudi direzione di design").click()
        page.get_by_role("button", name="Indiretti", exact=True).click()
        assert page.get_by_role("checkbox").count() == 3
        page.get_by_role("button", name="Tutti", exact=False).click()
        page.get_by_role("textbox", name="Cerca competitor").fill("not-present")
        assert page.get_by_role("heading", name="Nessun risultato").is_visible()
        page.get_by_role("button", name="Mostra tutti").click()
        page.get_by_role("button", name="Dettagli Forma Studio").click()
        assert page.get_by_role("complementary", name="Scheda competitor").get_by_role(
            "heading", name="Forma Studio").is_visible()
        page.get_by_role("button", name="Aggiungi competitor", exact=True).click()
        url = page.get_by_label("Sito web", exact=True)
        url.fill("http://example.test")
        page.get_by_role("button", name="Aggiungi", exact=True).click()
        assert page.get_by_role("alert").is_visible()
        url.fill("https://manual.test/")
        page.get_by_role("button", name="Aggiungi", exact=True).click()
        page.get_by_role("button", name="Chiudi aggiunta competitor").click()
        assert confirm.is_disabled()
        assert page.get_by_text("Verifica dei nuovi siti non ancora collegata.", exact=False).is_visible()
        page.get_by_role("button", name="Rimuovi", exact=True).click()
        assert confirm.is_enabled()
        confirm.click()
        assert page.get_by_text("Selezione di prova confermata in questa sessione.", exact=False).is_visible()
        assert page.get_by_role("button", name="Selezione confermata", exact=True).is_disabled()
        first.check()
        assert not page.get_by_text("Selezione di prova confermata in questa sessione.",
                                    exact=False).count()
        page.get_by_role("tab", name="Eventi aziendali", exact=True).click()
        assert page.get_by_role("checkbox", name="Includi Atlas Club").is_checked()
        assert confirm.is_enabled()
        page.get_by_role("tab", name="Eventi aziendali", exact=True).press("ArrowLeft")
        assert page.get_by_role("tab", name="Sport e tempo libero").get_attribute("aria-selected") == "true"
        page.set_viewport_size({"width": 390, "height": 844})
        page.get_by_role("button", name="Chiudi scheda", exact=True).click()
        first.uncheck()
        page.get_by_role("checkbox", name="Includi Spazio Uno", exact=True).check()
        assert confirm.is_enabled()
        assert page.get_by_role("checkbox", name="Includi Spazio Uno", exact=True).is_checked()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert page.get_by_role("table").bounding_box()["width"] > 300
        assert page.get_by_role("checkbox").count() == 7
        page.evaluate("window.scrollTo(0,0)")
        page.screenshot(path=str(artifacts / "mobile.png"), full_page=True)
        page.get_by_role("button", name="Dettagli Atlas Club", exact=True).click()
        assert page.get_by_role("complementary", name="Scheda competitor").is_visible()
        page.screenshot(path=str(artifacts / "mobile-detail.png"))
        page.get_by_role("button", name="Chiudi scheda", exact=True).click()
        page.reload()
        assert page.get_by_role("checkbox", name="Includi Atlas Club").is_checked()
        assert not posts and not errors and not external_requests
        browser.close()
