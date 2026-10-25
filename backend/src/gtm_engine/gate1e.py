"""Opt-in anonymous public-source pilot; no credential loading or paid requests."""

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import httpx

from gtm_engine.providers.public_sources import SAMPLES, PublicSourceError, download, normalize


def run(output: Path, client: httpx.Client) -> dict:
    probes = []
    report = {"version": "gate1e-v1", "gate_status": "IN_PROGRESS", "probes": probes,
              "limitations": ["Access samples, not validated market demand or buyer identities.",
                              "No fallback, automatic retry, credential or paid provider used."]}
    for source, (url, query) in SAMPLES.items():
        probe = {"source": source, "endpoint": url, "query": query,
                 "fetched_at": datetime.now(UTC).isoformat(), "status": "unavailable",
                 "provider_api_charge_usd": None if source == "openalex" else 0,
                 "local_compute_usd": None}
        try:
            body, metadata = download(client, source)
            probe.update(metadata)
            if metadata["status_code"] != 200:
                probe["reason"] = f"http_{metadata['status_code']}"
            else:
                raw = output / (source + ".raw")
                raw.write_bytes(body)
                probe.update(raw_reference=str(raw), sha256=hashlib.sha256(body).hexdigest())
                rows = normalize(source, body)
                if source == "openalex":
                    probe["provider_reported_cost_usd"] = json.loads(body).get("meta", {}).get(
                        "cost_usd")
                normalized = output / (source + ".normalized.json")
                normalized.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
                probe.update(status="available" if rows else "partial", records=len(rows),
                             normalized_reference=str(normalized),
                             normalization_version="public-sources-v2")
        except httpx.HTTPError:
            probe["reason"] = "network_unavailable"
        except PublicSourceError as error:
            probe["reason"] = str(error)
        probes.append(probe)
        (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["gate_status"] = "PASS_WITH_LIMITATIONS" if all(
        p["status"] == "available" for p in probes) else "PARTIAL"
    report["completed_at"] = datetime.now(UTC).isoformat()
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.live:
        print("Plan: four anonymous GETs, fixed official endpoints, no network or credentials.")
        return 0
    if not args.output:
        parser.error("A new private --output directory is required")
    output = args.output.resolve()
    ignored = subprocess.run(["git", "check-ignore", "-q", str(output / "report.json")],
                             capture_output=True, check=False)
    if ignored.returncode != 0:
        parser.error("Output must be ignored by Git")
    output.mkdir(parents=True, exist_ok=False)
    with httpx.Client(timeout=25, follow_redirects=False, trust_env=False,
                      headers={"User-Agent": "GTMEngineResearch/0.1"}) as client:
        report = run(output, client)
    print(json.dumps({"gate_status": report["gate_status"],
                      "sources": [{k: p.get(k) for k in
                                   ("source", "status", "status_code", "records", "reason")}
                                  for p in report["probes"]]}))
    return 0 if report["gate_status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
