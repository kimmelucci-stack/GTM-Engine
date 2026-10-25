import os
from pathlib import Path

import httpx
import pytest

from gtm_engine.gate1b import acceptance
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
