import hashlib
import os
from pathlib import Path

import httpx
import pytest

from gtm_engine.gate1b import acceptance, screening_summary, validate_mode
from gtm_engine.providers.web import CrawlError, WebsiteCrawler, parse_page, public_dns, safe_url

HTML = """<html><body><nav><p>€ 99999</p></nav><main>
<h1>Team building di esempio</h1><p>Pacchetto a partire da € 120 per persona.</p>
<p>Case study dimostrativo, privo di risultati commerciali reali.</p>
<p>Attività di gruppo per aziende: questo testo sintetico verifica l'estrazione
di informazioni commerciali con fonti, senza confondere dichiarazioni e prove.</p>
<a href='/servizi'>Scopri le attività</a><a href='https://elsewhere.test/servizi'>Esterno</a>
</main><script>secret</script></body></html>"""


@pytest.mark.parametrize("url", ["http://example.test",
                                   "https://" + "fixture-user:fixture-value@" + "example.test/",
                                   "https://example.test/?token=x", "https://127.0.0.1/",
                                   "https://example.test:8000/"])
def test_reject_unsafe_urls(url):
    with pytest.raises(CrawlError):
        safe_url(url, {"example.test"})


def test_observations_are_sourced_not_asserted_truth():
    evidence, _, text = parse_page(HTML, "https://example.test/", "2026-10-25", "private.html")
    assert {e.field for e in evidence} >= {"published_price", "publisher_claim", "cta"}
    assert all(e.source_url and e.raw_reference and e.nature == "observed" for e in evidence)
    assert all("99999" not in e.text and "secret" not in e.text for e in evidence)
    assert "secret" not in text


def crawler(tmp_path: Path, handler, **kwargs):
    return WebsiteCrawler("https://example.test/", tmp_path, max_pages=2,
                          client=httpx.Client(transport=httpx.MockTransport(handler)),
                          resolve=lambda _: None, pause=lambda _: None, **kwargs)


def test_crawl_caps_and_missing_values(tmp_path):
    def handler(request):
        return httpx.Response(200, text="User-agent: *\nAllow: /" if
                              request.url.path == "/robots.txt" else HTML,
                              headers={"content-type": "text/html"})
    result = crawler(tmp_path, handler).crawl()
    assert len(result["pages"]) == 2
    assert result["requests"] == 3
    assert all(p["status"] == "available" for p in result["pages"])
    assert all("elsewhere" not in link for p in result["pages"] for link in p["links"])
    assert all(Path(p["raw_reference"]).exists() for p in result["pages"])
    assert all(hashlib.sha256(Path(p["raw_reference"]).read_bytes()).hexdigest() == p["sha256"]
               for p in result["pages"])


def test_disallowed_robots_never_fetches_content(tmp_path):
    paths = []

    def handler(request):
        paths.append(request.url.path)
        return httpx.Response(200, text="User-agent: *\nDisallow: /")
    result = crawler(tmp_path, handler).crawl()
    assert paths == ["/robots.txt"]
    assert result["pages"][0]["reason"] == "robots_disallowed"


def test_redirect_private_target_blocked(tmp_path):
    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(302, headers={"location": "https://127.0.0.1/private"})
    result = crawler(tmp_path, handler).crawl()
    assert result["pages"][0]["reason"] == "url_not_allowed"


def test_timeout_is_unavailable_and_does_not_leak_exception(tmp_path):
    def handler(request):
        raise httpx.ReadTimeout("private upstream detail")
    result = crawler(tmp_path, handler).crawl()
    assert result["pages"][0]["reason"] == "network_unavailable"
    assert result["pages"][0]["evidence"] == []


def test_robots_unknown_is_fail_closed(tmp_path):
    result = crawler(tmp_path, lambda _: httpx.Response(503)).crawl()
    assert result["pages"][0]["status"] == "unavailable"
    assert result["requests"] == 1


def test_no_price_does_not_become_zero():
    evidence, _, _ = parse_page("<h1>Attività di gruppo su preventivo</h1>", "url", "date", "raw")
    assert not any(e.field == "published_price" for e in evidence)


def test_split_price_preserves_offer_context_and_tax_basis():
    html = """<main><div>Mezza giornata, fino a 30 persone
    <span>€</span><strong>200,00</strong><span> + IVA</span></div>
    <table><tr><td>Giornata intera</td><td>€ 350,00 + IVA</td></tr></table></main>"""
    evidence, _, _ = parse_page(html, "https://example.test/pricing", "date", "raw")
    prices = [e for e in evidence if e.field == "published_price"]
    assert any("Mezza giornata" in e.text and "200,00" in e.text and "IVA" in e.text
               for e in prices)
    assert any("Giornata intera" in e.text and "350,00" in e.text for e in prices)


def test_long_cms_paragraph_keeps_bounded_price_evidence():
    html = "<p>" + "Introduzione senza prezzo. " * 40
    html += "<br>Mezza giornata fino a 30 persone: € 200,00 + IVA."
    html += "<br>Condizioni aggiuntive. " * 40 + "</p>"
    evidence, _, _ = parse_page(html, "https://example.test/pricing", "date", "raw")
    prices = [e for e in evidence if e.field == "published_price"]
    assert prices and all(len(e.text) <= 500 for e in prices)
    assert any("Mezza giornata" in e.text and "IVA" in e.text for e in prices)


def test_screening_does_not_promote_access_to_gate_approval():
    sites = [{"root": f"https://site{i}.test", "pages": [
        {"status": "available", "evidence": [{"field": "publisher_claim"}]}]}
        for i in range(5)]
    result = screening_summary(sites)
    assert result["websites_with_evidence"] == 5
    assert result["gate_status"] == "AWAITING_SAMPLE_APPROVAL"
    assert result["sample_confirmed"] is False
    sites[0]["pages"][0]["status"] = "unavailable"
    assert screening_summary(sites)["screening_status"] == "partial"


def test_screening_cannot_use_browser_or_confirm_sample():
    urls = ["https://example.test/"]
    validate_mode(urls, screen=True, confirmed=False, browser=False)
    for confirmed, browser in ((True, False), (False, True)):
        with pytest.raises(ValueError):
            validate_mode(urls, screen=True, confirmed=confirmed, browser=browser)
    with pytest.raises(ValueError):
        validate_mode(urls, screen=False, confirmed=False, browser=False)
    with pytest.raises(ValueError):
        validate_mode(urls + ["https://www.example.test/path"], screen=True,
                      confirmed=False, browser=False)
    with pytest.raises(ValueError):
        validate_mode([f"https://site{i}.test/" for i in range(17)], screen=True,
                      confirmed=False, browser=False)


def test_request_cap_applies_to_robots_and_content(tmp_path):
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(404)
    result = crawler(tmp_path, handler, max_requests=1).crawl()
    assert len(seen) == 1
    assert result["pages"][0]["reason"] == "request_limit"


def test_gate_requires_five_successful_sites_and_owner_confirmation():
    sites = [{"root": f"https://site{i}.test", "pages": [{"status": "available", "evidence": [1]}]}
             for i in range(5)]
    assert acceptance(sites, False) == "AWAITING_SAMPLE_APPROVAL"
    assert acceptance(sites[:4], True) == "NOT_PASSED"
    assert acceptance(sites, True) == "PASS_WITH_LIMITATIONS"
    sites[0]["pages"][0]["status"] = "unavailable"
    assert acceptance(sites, True) == "NOT_PASSED"


def test_oversized_response_is_unavailable(tmp_path):
    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, content=b"x" * 2_000_001,
                              headers={"content-type": "text/html"})
    assert crawler(tmp_path, handler).crawl()["pages"][0]["reason"] == "response_too_large"


def test_dns_rejects_mixed_public_private_results(monkeypatch):
    monkeypatch.setattr("socket.getaddrinfo", lambda *a, **kw: [
        (2, 1, 6, "", ("93.184.216.34", 443)), (2, 1, 6, "", ("10.0.0.1", 443))])
    with pytest.raises(CrawlError, match="non_public_destination"):
        public_dns("https://example.test/")


def test_challenge_is_not_claim_evidence(tmp_path):
    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, text="<title>Just a moment...</title><h1>Verify human</h1>",
                              headers={"content-type": "text/html"})
    result = crawler(tmp_path, handler).crawl()["pages"][0]
    assert result["reason"] == "access_challenge"
    assert result["evidence"] == []
    assert set(result["fields"].values()) == {"unavailable"}


def test_browser_fallback_only_for_thin_successful_html(tmp_path, monkeypatch):
    def handler(request):
        return httpx.Response(404) if request.url.path == "/robots.txt" else httpx.Response(
            200, text="<html><main id='app'></main></html>", headers={"content-type": "text/html"})
    monkeypatch.setattr(WebsiteCrawler, "render", lambda self, url: HTML)
    result = crawler(tmp_path, handler, browser=True).crawl()
    assert result["pages"][0]["method"] == "playwright"
    assert result["pages"][0]["status"] == "available"


@pytest.mark.skipif(os.environ.get("GTM_BROWSER_TEST") != "1", reason="Opt-in Chromium test")
def test_real_chromium_renders_synthetic_dynamic_page(tmp_path):
    import json
    shell = "<html><body><main id='app'></main><script>document.getElementById('app').innerHTML="
    shell += json.dumps(HTML).replace("</", "<\\/") + ";</script></body></html>"

    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(200, text=shell, headers={"content-type": "text/html"})
    result = crawler(tmp_path, handler, browser=True).crawl()
    assert result["pages"][0]["method"] == "playwright"
    assert result["pages"][0]["evidence"]
