"""KB-001 opt-in bounded checks for an explicitly approved source registry."""

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import httpx
from pydantic import ValidationError

from gtm_engine.domain.source_refresh import SourceRecord, due
from gtm_engine.providers.web import CrawlError, public_dns

MAX_BYTES = 2_000_000


def check_sources(sources: list[SourceRecord], client: httpx.Client, *, now: datetime,
                  live: bool = False, request_cap: int = 20, resolve=public_dns) -> dict:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Calendar clock requires timezone")
    now = now.astimezone(UTC)
    if not 1 <= request_cap <= 100:
        raise ValueError("Request cap must be 1..100")
    if len({s.source_id for s in sources}) != len(sources):
        raise ValueError("Duplicate source ID")
    rows, updated, requests = [], [], 0
    for source in sources:
        row = {"source_id": source.source_id, "status": "not_due", "http_status": None}
        next_source = source.model_copy(deep=True)
        if source.status != "approved":
            row["status"] = "not_approved"
        elif source.last_checked_at and source.last_checked_at > now:
            row["status"] = "invalid_future_check"
        elif due(source, now):
            row["status"] = "due" if not live else "deferred_limit"
            if live and requests < request_cap:
                next_source.last_attempted_at = now
                headers = {}
                if source.etag:
                    headers["If-None-Match"] = source.etag
                if source.last_modified:
                    headers["If-Modified-Since"] = source.last_modified
                try:
                    resolve(source.url)
                    requests += 1
                    with client.stream("GET", source.url, headers=headers) as response:
                        row["http_status"] = response.status_code
                        if response.status_code == 304:
                            if not source.sha256 or not headers:
                                raise CrawlError("unverifiable_304")
                            row["status"] = "unchanged"
                            next_source.etag = response.headers.get("etag", source.etag)
                            next_source.last_modified = response.headers.get(
                                "last-modified", source.last_modified)
                        elif response.status_code == 200:
                            body = bytearray()
                            for chunk in response.iter_bytes():
                                body.extend(chunk)
                                if len(body) > MAX_BYTES:
                                    raise CrawlError("response_too_large")
                            # A 200 challenge/error page is not a successful source check.
                            if not body:
                                raise CrawlError("empty_response")
                            content = bytes(body).lower()
                            if any(marker in content for marker in (
                                b"<title>just a moment", b"<title>access denied",
                                b"<title>server temporarily unavailable")):
                                raise CrawlError("source_challenge_or_error_page")
                            digest = hashlib.sha256(body).hexdigest()
                            row["status"] = ("initial" if source.sha256 is None else
                                             "unchanged" if digest == source.sha256 else "changed")
                            next_source.sha256 = digest
                            next_source.etag = response.headers.get("etag")
                            next_source.last_modified = response.headers.get("last-modified")
                        else:
                            raise CrawlError(f"http_{response.status_code}")
                    next_source.last_checked_at = now
                    next_source.last_error = None
                except httpx.HTTPError:
                    row.update(status="unavailable", reason="network_unavailable")
                    next_source.last_error = "network_unavailable"
                except CrawlError as error:
                    row.update(status="unavailable", reason=str(error))
                    next_source.last_error = str(error)
                except ValueError:
                    row.update(status="unavailable", reason="invalid_request_metadata")
                    next_source.last_error = "invalid_request_metadata"
        rows.append(row)
        updated.append(next_source.model_dump(mode="json"))
    return {"version": "kb-001-v1", "checked_at": now.isoformat(), "live": live,
            "network_requests": requests, "checks": rows, "registry": updated,
            "cost": {"provider_charge_usd": None, "local_compute_usd": None},
            "limitations": ["Changed hash is a review signal, not a semantic change verdict.",
                            "Execution cost and external quotas are not measured by this checker.",
                            "No playbook rewritten or source approved by this check.",
                            "CLI only; DNS check is not socket pinning. Not an arbitrary-URL API."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--request-cap", type=int, default=20)
    args = parser.parse_args()
    try:
        sources = [SourceRecord.model_validate(row) for row in
                   json.loads(args.registry.read_text(encoding="utf-8-sig"))]
        if len(sources) > 1000:
            raise ValueError
    except (OSError, ValueError, TypeError, ValidationError):
        parser.error("Invalid registry; values withheld")
    output = args.output.resolve()
    ignored = subprocess.run(["git", "check-ignore", "-q", str(output / "report.json")],
                             capture_output=True, check=False)
    if ignored.returncode != 0:
        parser.error("Output must be ignored by Git")
    output.mkdir(parents=True, exist_ok=False)
    with httpx.Client(timeout=20, follow_redirects=False, trust_env=False,
                      headers={"User-Agent": "GTMEngineSourceCheck/0.1"}) as client:
        try:
            report = check_sources(sources, client, now=datetime.now(UTC), live=args.live,
                                   request_cap=args.request_cap)
        except ValueError:
            parser.error("Invalid calendar or duplicate identities; values withheld")
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output / "registry.next.json").write_text(json.dumps(report["registry"], indent=2),
                                              encoding="utf-8")
    print(json.dumps({"network_requests": report["network_requests"],
                      "statuses": [row["status"] for row in report["checks"]]}))
    return 1 if any(r["status"] in ("unavailable", "invalid_future_check", "deferred_limit")
                   for r in report["checks"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
