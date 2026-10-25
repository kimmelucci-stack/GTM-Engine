import io
import json
import zipfile

import httpx
import pytest

from gtm_engine.providers.public_sources import (
    PublicSourceError,
    ateco_rows,
    download,
    eurostat_rows,
    normalize,
)


def test_sparse_jsonstat_preserves_zero_missing_period_and_dimensions():
    data = {"class": "dataset", "id": ["geo", "time"], "size": [1, 2],
            "dimension": {"geo": {"category": {"index": {"IT": 0}}},
                          "time": {"category": {"index": {"2024": 1, "2023": 0}}}},
            "value": {"0": 0}, "status": {"0": "p"}, "updated": "synthetic"}
    rows = eurostat_rows(data)
    assert rows[0]["value"] == 0
    assert rows[0]["status_flag"] == "p"
    assert rows[0]["dimensions"] == {"geo": "IT", "time": "2023"}
    assert rows[1]["value"] is None


def test_import_finds_classification_sheet_and_preserves_leading_zero():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("xl/worksheets/sheet1.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>')
        archive.writestr("xl/worksheets/sheet2.xml", '''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
          <row><c r="B1" t="inlineStr"><is><t>CODICE_ATECO_2025</t></is></c>
          <c r="C1" t="inlineStr"><is><t>TITOLO_ITALIANO_ATECO_2025</t></is></c></row>
          <row><c r="B2" t="inlineStr"><is><t>01.11.00</t></is></c>
          <c r="C2" t="inlineStr"><is><t>Synthetic title</t></is></c></row>
        </sheetData></worksheet>''')
    assert ateco_rows(buffer.getvalue())[0]["code"] == "01.11.00"


def test_html_error_is_not_a_valid_api_or_workbook():
    with pytest.raises(PublicSourceError):
        normalize("openalex", b"<html>unavailable</html>")
    with pytest.raises(PublicSourceError):
        ateco_rows(b"<html>unavailable</html>")


@pytest.mark.parametrize("status", [302, 307, 429])
def test_redirect_and_rate_limit_are_not_followed_or_retried(status):
    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(status, headers={"location": "https://unapproved.test/"})

    with httpx.Client(transport=httpx.MockTransport(respond), follow_redirects=False) as client:
        body, meta = download(client, "openalex")
    assert len(seen) == 1
    assert meta["status_code"] == status and body == b""
    assert "authorization" not in seen[0].headers


def test_empty_results_are_not_fabricated():
    assert normalize("openalex", json.dumps({"results": []}).encode()) == []
    with pytest.raises(PublicSourceError):
        normalize("openalex", json.dumps({"results": [{"title": "Missing ID"}]}).encode())


def test_gate_reports_unavailable_sources_without_passing(tmp_path):
    from gtm_engine.gate1e import run

    seen = []

    def unavailable(request):
        seen.append(request)
        return httpx.Response(503)

    with httpx.Client(transport=httpx.MockTransport(unavailable)) as client:
        report = run(tmp_path, client)
    assert len(seen) == 4
    assert report["gate_status"] == "PARTIAL"
    assert all(p["status"] == "unavailable" for p in report["probes"])
    assert all(p["reason"] == "http_503" for p in report["probes"])
    assert json.loads((tmp_path / "report.json").read_text())["gate_status"] == "PARTIAL"


def test_response_size_cap(monkeypatch):
    monkeypatch.setattr("gtm_engine.providers.public_sources.MAX_BYTES", 3)
    transport = httpx.MockTransport(lambda r: httpx.Response(200, content=b"1234"))
    with (httpx.Client(transport=transport) as client,
          pytest.raises(PublicSourceError, match="response_too_large")):
        download(client, "openalex")
