import hashlib
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from pydantic import ValidationError

from gtm_engine.domain.source_refresh import SourceRecord, due
from gtm_engine.providers.web import CrawlError
from gtm_engine.source_refresh import check_sources

NOW = datetime(2026, 10, 25, 12, tzinfo=UTC)
BODY = b"Synthetic source content"
DIGEST = hashlib.sha256(BODY).hexdigest()


def source(**overrides):
    return SourceRecord(**({"source_id": "synthetic", "title": "Synthetic source",
                            "publisher": "Fixture", "url": "https://source.test/reference",
                            "methodology_notes": "Fixture, no real approval",
                            "applicability": "Synthetic tests only", "status": "approved"}
                           | overrides))


def run(record, handler, **options):
    with httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False) as client:
        return check_sources([record], client, now=NOW, resolve=lambda u: None, **options)


@pytest.mark.parametrize("days,expected", [(44, False), (45, True), (46, True)])
def test_calendar_boundary(days, expected):
    assert due(source(last_checked_at=NOW-timedelta(days=days)), NOW) is expected


def test_missing_check_is_due_but_draft_is_not():
    assert due(source(), NOW)
    assert not due(source(status="draft"), NOW)


def test_offline_calendar_never_calls_transport_or_dns():
    def forbidden(*args):
        pytest.fail("Offline calendar used network")

    with httpx.Client(transport=httpx.MockTransport(forbidden)) as client:
        report = check_sources([source()], client, now=NOW, resolve=forbidden)
    assert report["network_requests"] == 0
    assert report["checks"][0]["status"] == "due"
    assert report["registry"][0]["last_checked_at"] is None


@pytest.mark.parametrize("kwargs", [
    {"last_checked_at": NOW-timedelta(days=44)}, {"status": "draft"},
    {"status": "deprecated"}, {"last_checked_at": NOW+timedelta(days=1)},
])
def test_not_due_or_unapproved_source_does_not_make_requests(kwargs):
    def forbidden(request):
        pytest.fail("Unexpected HTTP call")

    report = run(source(**kwargs), forbidden, live=True)
    assert report["network_requests"] == 0


def test_conditional_304_preserves_hash_and_updates_success_clock():
    def handler(request):
        assert request.headers["If-None-Match"] == '"v1"'
        assert request.headers["If-Modified-Since"] == "Wed, 01 Jul 2026 12:00:00 GMT"
        return httpx.Response(304)

    record = source(last_checked_at=NOW-timedelta(days=45), sha256=DIGEST,
                    etag='"v1"', last_modified="Wed, 01 Jul 2026 12:00:00 GMT")
    report = run(record, handler, live=True)
    result = SourceRecord.model_validate(report["registry"][0])
    assert report["checks"][0]["status"] == "unchanged"
    assert result.last_checked_at == NOW and result.sha256 == DIGEST
    assert record.last_checked_at != NOW  # Input not silently mutated.


@pytest.mark.parametrize("digest,status", [(None, "initial"), (DIGEST, "unchanged"),
                                          ("a"*64, "changed")])
def test_200_hash_comparison_and_stale_validators_removed(digest, status):
    report = run(source(sha256=digest, etag='"old"'),
                 lambda r: httpx.Response(200, content=BODY), live=True)
    assert report["checks"][0]["status"] == status
    assert report["registry"][0]["etag"] is None
    assert report["registry"][0]["sha256"] == DIGEST


@pytest.mark.parametrize("status,content", [
    (429, b""), (503, b""), (302, b""), (304, b""), (200, b""),
    (200, b"<title>Just a moment...</title>"),
])
def test_failure_keeps_success_clock_and_records_separate_attempt(status, content):
    record = source(last_checked_at=NOW-timedelta(days=46))
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, content=content,
                              headers={"location": "https://other.test/"})

    report = run(record, handler, live=True)
    updated = SourceRecord.model_validate(report["registry"][0])
    assert len(calls) == 1
    assert report["checks"][0]["status"] == "unavailable"
    assert updated.last_checked_at == record.last_checked_at
    assert updated.last_attempted_at == NOW and updated.last_error


def test_timeout_does_not_leak_remote_exception_or_refresh_success():
    report = run(source(), lambda r: (_ for _ in ()).throw(
        httpx.ReadTimeout("synthetic-sensitive-text")), live=True)
    assert report["checks"][0]["reason"] == "network_unavailable"
    assert "synthetic-sensitive-text" not in str(report)


def test_request_cap_defers_rest_and_keeps_unattempted_timestamps():
    with httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, content=BODY))) as client:
        report = check_sources([source(), source(source_id="second")], client, now=NOW,
                               live=True, request_cap=1, resolve=lambda u: None)
    assert report["network_requests"] == 1
    assert report["checks"][1]["status"] == "deferred_limit"
    assert report["registry"][1]["last_attempted_at"] is None


def test_private_dns_blocks_http():
    def reject(url):
        raise CrawlError("non_public_destination")

    with httpx.Client(transport=httpx.MockTransport(lambda r: pytest.fail("Unexpected HTTP"))) as client:
        report = check_sources([source()], client, now=NOW, live=True, resolve=reject)
    assert report["network_requests"] == 0
    assert report["checks"][0]["reason"] == "non_public_destination"


@pytest.mark.parametrize("url", ["http://source.test/",
                                 "https://" + "synthetic-user:synthetic-password" + "@source.test/",
                                 "https://source.test/?access_token=synthetic"])
def test_registry_rejects_non_https_or_credential_urls(url):
    with pytest.raises(ValidationError):
        source(url=url)


def test_timezone_required_and_duplicate_ids_rejected():
    with pytest.raises(ValidationError):
        source(last_checked_at=datetime(2026, 10, 25))
    with httpx.Client() as client, pytest.raises(ValueError, match="Duplicate"):
        check_sources([source(), source()], client, now=NOW)


def test_oversized_content_keeps_previous_verification(monkeypatch):
    monkeypatch.setattr("gtm_engine.source_refresh.MAX_BYTES", 2)
    record = source(last_checked_at=NOW-timedelta(days=45), sha256=DIGEST)
    report = run(record, lambda r: httpx.Response(200, content=BODY), live=True)
    assert report["checks"][0]["reason"] == "response_too_large"
    assert report["registry"][0]["sha256"] == DIGEST
    assert SourceRecord.model_validate(report["registry"][0]).last_checked_at == record.last_checked_at
