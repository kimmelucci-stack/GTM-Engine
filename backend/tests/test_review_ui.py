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
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors = []
        posts = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("request", lambda request: posts.append(request.url)
                if request.method == "POST" else None)
        page.goto("http://127.0.0.1:5173/")
        page.get_by_role("button", name="Apri esempio interattivo").click()
        confirm = page.get_by_role("button", name="Conferma selezione di prova")
        assert confirm.is_enabled()
        first = page.get_by_role("checkbox", name="Operatore di esempio 1", exact=False)
        first.uncheck()
        assert confirm.is_disabled()
        page.get_by_role("checkbox", name="Operatore di esempio 6", exact=False).check()
        assert confirm.is_enabled()
        page.get_by_role("checkbox", name="Operatore di esempio 7", exact=False).check()
        assert confirm.is_disabled()
        page.get_by_role("checkbox", name="Operatore di esempio 7", exact=False).uncheck()
        page.screenshot(path=str(artifacts / "desktop.png"), full_page=True)
        page.get_by_text("Aggiungi un competitor tramite sito web", exact=True).click()
        url = page.get_by_label("Sito del competitor")
        url.fill("http://example.test")
        page.get_by_role("button", name="Aggiungi", exact=True).click()
        assert page.get_by_role("alert").is_visible()
        url.fill("https://manual.test/")
        page.get_by_role("button", name="Aggiungi", exact=True).click()
        assert confirm.is_disabled()
        assert page.get_by_text("Verifica dei nuovi siti non ancora collegata.", exact=False).is_visible()
        page.get_by_role("button", name="Rimuovi", exact=True).click()
        assert confirm.is_enabled()
        confirm.click()
        assert page.get_by_text("Selezione di prova confermata in questa sessione.", exact=False).is_visible()
        assert confirm.is_disabled()
        first.check()
        assert not page.get_by_text("Selezione di prova confermata in questa sessione.",
                                    exact=False).count()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.screenshot(path=str(artifacts / "mobile.png"), full_page=True)
        page.reload()
        assert page.get_by_role("button", name="Apri esempio interattivo").is_visible()
        assert not posts and not errors
        browser.close()
