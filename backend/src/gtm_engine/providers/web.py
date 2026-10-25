"""Bounded, anonymous website pilot. Never authenticates or bypasses access controls."""

from __future__ import annotations

import hashlib
import ipaddress
import re
import socket
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx
import trafilatura
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

USER_AGENT = "GTMEngineResearch/0.1"
MAX_BYTES = 2_000_000
WEB_EXTRACTOR_VERSION = "web-extract-v2"
RELEVANT = re.compile(r"serviz|team.?build|prezz|pric|case|client|testimon|chi-siamo|about", re.IGNORECASE)
PRICE = re.compile(r"(?:€\s*\d[\d.,]*|\d[\d.,]*\s*(?:€|euro))", re.IGNORECASE)


class CrawlError(Exception):
    """Only fixed error codes should cross the provider boundary."""


def safe_url(url: str, hosts: set[str]) -> str:
    p = urlsplit(url)
    if (p.scheme != "https" or p.hostname not in hosts or p.username or p.password
            or p.port not in (None, 443) or p.query):
        raise CrawlError("url_not_allowed")
    return urlunsplit((p.scheme, p.netloc, p.path or "/", "", ""))


def public_dns(url: str) -> None:
    """Validate each destination, including every redirect. No private network targets."""
    try:
        addresses = socket.getaddrinfo(urlsplit(url).hostname, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise CrawlError("non_public_destination")
    except OSError:
        raise CrawlError("dns_unavailable") from None


class Evidence(BaseModel):
    field: str
    text: str
    source_url: str
    fetched_at: str
    raw_reference: str
    nature: str = "observed"
    limitation: str = "Publisher statement; not independently verified."


class Page(BaseModel):
    requested_url: str
    source_url: str
    fetched_at: str
    status: str
    status_code: int | None = None
    method: str = "http"
    reason: str | None = None
    raw_reference: str | None = None
    sha256: str | None = None
    text_length: int = 0
    evidence: list[Evidence] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    fields: dict[str, str] = Field(default_factory=dict)


def parse_page(html: str, url: str, timestamp: str, raw: str) -> tuple[list[Evidence], list[str], str]:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "nav", "footer", "header", "noscript", "form"]):
        node.decompose()
    text = trafilatura.extract(str(soup), include_comments=False, include_tables=True) or ""
    records: list[Evidence] = []
    seen: set[tuple[str, str]] = set()
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li", "a", "button",
                              "div", "span", "strong", "td", "tr", "dd"]):
        snippet = " ".join(tag.stripped_strings)
        if len(snippet) > 500 and tag.name in ("p", "li", "td", "dd"):
            # Some CMSs put an entire tariff in a single paragraph with <br>.
            # Keep bounded contiguous excerpts around prices rather than
            # dropping the paragraph or inferring an offer from a bare amount.
            for match in PRICE.finditer(snippet):
                start = max(0, match.start() - 180)
                end = min(len(snippet), match.end() + 180)
                excerpt = snippet[start:end].strip()
                key = ("published_price", excerpt)
                if key not in seen:
                    records.append(Evidence(
                        field="published_price", text=excerpt, source_url=url,
                        fetched_at=timestamp, raw_reference=raw,
                        limitation="Contiguous price excerpt; verify full terms and validity on source."
                    ))
                    seen.add(key)
            continue
        if not 8 <= len(snippet) <= 500:
            continue
        field = None
        if PRICE.search(snippet):
            field = "published_price"
        elif tag.name in ("h1", "h2", "h3"):
            field = "publisher_claim"
        elif re.search(r"case stud|caso studio|testimonianz", snippet, re.IGNORECASE):
            field = "case_study_mention"
        elif tag.name in ("a", "button") and re.search(
            r"contatt|preventivo|scopri|prenot|richied", snippet, re.IGNORECASE
        ):
            field = "cta"
        if field and (field, snippet) not in seen:
            records.append(Evidence(field=field, text=snippet, source_url=url,
                                    fetched_at=timestamp, raw_reference=raw))
            seen.add((field, snippet))
    links = sorted({urldefrag(urljoin(url, a["href"]))[0]
                    for a in soup.find_all("a", href=True) if RELEVANT.search(a["href"])})
    # Preserve published prices when the page contains many decorative headings.
    # This is extraction ordering, never a competitor ranking or numeric estimate.
    records.sort(key=lambda record: record.field != "published_price")
    return records[:80], links, text


class WebsiteCrawler:
    """CLI pilot only: not exposed to untrusted API input.

    DNS is checked before requests, not pinned to sockets. Deployment needs an
    egress firewall/pinned transport before accepting arbitrary user URLs.
    """

    def __init__(self, root: str, output: Path, *, max_pages: int = 4,
                 client: httpx.Client | None = None, resolve=public_dns,
                 pause=time.sleep, browser: bool = False, max_requests: int | None = None):
        host = urlsplit(root).hostname or ""
        domain = host.removeprefix("www.")
        self.hosts = {domain, "www." + domain}
        self.root = safe_url(root, self.hosts)
        if not 1 <= max_pages <= 8:
            raise ValueError("max_pages must be 1..8")
        self.max_pages, self.output = max_pages, output
        self.max_requests = max_requests if max_requests is not None else max_pages * 5 + 10
        if not 1 <= self.max_requests <= 50:
            raise ValueError("max_requests must be 1..50")
        self.output.mkdir(parents=True, exist_ok=True)
        self.client = client or httpx.Client(timeout=20, follow_redirects=False, trust_env=False,
                                            headers={"User-Agent": USER_AGENT})
        self.resolve, self.pause, self.browser = resolve, pause, browser
        self.requests = 0
        self.cache: dict[str, tuple[str, int, str]] = {}
        self.request_log: list[dict] = []
        self.robots: dict[str, RobotFileParser] = {}
        self.delay = 1.0

    def get(self, url: str, *, robots: bool = False,
            resource: bool = False) -> tuple[str, int, str]:
        for _ in range(4):
            url = safe_url(url, self.hosts)
            self.resolve(url)
            if not robots and not self.allowed(url):
                raise CrawlError("robots_disallowed")
            if url in self.cache:
                return self.cache[url]
            if self.requests >= self.max_requests:
                raise CrawlError("request_limit")
            self.pause(self.delay)
            self.requests += 1
            try:
                with self.client.stream("GET", url) as response:
                    code = response.status_code
                    self.request_log.append({"url": url, "status_code": code,
                                             "at": datetime.now(UTC).isoformat(),
                                             "robots": robots})
                    if code in (301, 302, 303, 307, 308):
                        url = urljoin(url, response.headers.get("location", ""))
                        continue
                    if robots and code == 404:
                        self.cache[url] = (url, code, "")
                        return url, code, ""
                    if code != 200:
                        raise CrawlError(f"http_{code}")
                    if (not robots and not resource
                            and "html" not in response.headers.get("content-type", "")):
                        raise CrawlError("not_html")
                    body = bytearray()
                    for chunk in response.iter_bytes():
                        body.extend(chunk)
                        if len(body) > MAX_BYTES:
                            raise CrawlError("response_too_large")
                    decoded = bytes(body).decode(response.encoding or "utf-8", "replace")
                    self.cache[url] = (url, code, decoded)
                    if robots:
                        host = urlsplit(url).hostname
                        (self.output / f"robots-{host}.txt").write_text(decoded, encoding="utf-8")
                    return url, code, decoded
            except httpx.HTTPError:
                raise CrawlError("network_unavailable") from None
        raise CrawlError("redirect_limit")

    def allowed(self, url: str) -> bool:
        p = urlsplit(url)
        origin = f"{p.scheme}://{p.netloc}"
        if origin not in self.robots:
            _, _, body = self.get(origin + "/robots.txt", robots=True)
            parser = RobotFileParser()
            parser.parse(body.splitlines())
            delay = parser.crawl_delay(USER_AGENT) or parser.crawl_delay("*") or 1
            if delay > 10:
                raise CrawlError("crawl_delay_exceeds_pilot_limit")
            self.robots[origin] = parser
            self.delay = max(self.delay, delay)
        return self.robots[origin].can_fetch(USER_AGENT, url)

    def render(self, url: str) -> str:
        # All browser traffic uses the same checked HTTP transport: redirects,
        # robots, size and request caps apply to scripts/XHR as well as documents.
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise CrawlError("browser_unavailable") from None
        from playwright.sync_api import Error

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context(service_workers="block", accept_downloads=False,
                                              user_agent=USER_AGENT)

                def route_request(route):
                    request = route.request
                    if request.method != "GET" or request.resource_type not in (
                        "document", "script", "xhr", "fetch"
                    ):
                        route.abort()
                        return
                    try:
                        _, code, body = self.get(request.url, resource=True)
                        content_type = {"script": "application/javascript",
                                        "xhr": "application/json", "fetch": "application/json"}
                        route.fulfill(status=code, body=body,
                                      content_type=content_type.get(request.resource_type,
                                                                    "text/html"))
                    except CrawlError:
                        route.abort()

                context.route("**/*", route_request)
                context.route_web_socket("**/*", lambda ws: ws.close())
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1500)
                html = page.content()
                context.close()
                browser.close()
                if len(html.encode()) > MAX_BYTES:
                    raise CrawlError("render_too_large")
                return html
        except Error:
            raise CrawlError("browser_unavailable") from None

    def crawl(self) -> dict:
        pages: list[Page] = []
        queue, visited = [self.root], set()
        while queue and len(pages) < self.max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            stamp = datetime.now(UTC).isoformat()
            page = Page(requested_url=url, source_url=url, fetched_at=stamp, status="unavailable")
            page.fields = dict.fromkeys(
                ("published_price", "publisher_claim", "case_study_mention", "cta"), "unavailable"
            )
            try:
                final, code, html = self.get(url)
                page.source_url, page.status_code = final, code
                title = BeautifulSoup(html, "html.parser").title
                if title and re.search(r"just a moment|access denied|verify.*human|captcha",
                                       title.get_text(), re.IGNORECASE):
                    raise CrawlError("access_challenge")
                raw = self.output / f"page-{len(pages) + 1}.html"
                evidence, links, text = parse_page(html, final, stamp, str(raw))
                if len(text) < 100 and self.browser:
                    html = self.render(final)
                    page.method = "playwright"
                    evidence, links, text = parse_page(html, final, stamp, str(raw))
                # Stable snapshot bytes on Windows and Linux; no newline translation.
                raw.write_bytes(html.encode("utf-8"))
                page.raw_reference = str(raw)
                page.sha256 = hashlib.sha256(html.encode()).hexdigest()
                page.evidence, page.text_length = evidence, len(text)
                page.status = "available" if len(text) >= 100 else "partial"
                page.reason = None if page.status == "available" else "insufficient_text"
                for field in ("published_price", "publisher_claim", "case_study_mention", "cta"):
                    page.fields[field] = (
                        "observed" if any(e.field == field for e in evidence)
                        else "unavailable_in_sample"
                    )
                for link in links:
                    try:
                        checked = safe_url(link, self.hosts)
                        page.links.append(checked)
                        if checked not in visited and checked not in queue:
                            queue.append(checked)
                    except (CrawlError, ValueError):
                        continue
            except (CrawlError, ValueError) as error:
                page.reason = str(error) if isinstance(error, CrawlError) else "invalid_url"
                if page.reason.startswith("http_"):
                    page.status_code = int(page.reason.removeprefix("http_"))
            pages.append(page)
        return {"root": self.root, "provider": "anonymous_website", "version": "gate1b-v1",
                "extractor_version": WEB_EXTRACTOR_VERSION,
                "requests": self.requests, "max_pages": self.max_pages,
                "max_requests": self.max_requests,
                "request_log": self.request_log,
                "pages": [p.model_dump() for p in pages],
                "cost": {"provider_api_usd": 0, "local_compute_usd": None},
                "limitations": ["Bounded sample, not whole-site coverage.",
                                "Claims are publisher statements, not proven outcomes.",
                                "Absence in sample does not establish absence on website."]}
