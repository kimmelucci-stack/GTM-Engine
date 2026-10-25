"""Opt-in private competitor crawl. No API credentials are read."""

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from gtm_engine.providers.web import WebsiteCrawler


def acceptance(sites: list[dict], confirmed: bool) -> str:
    if not confirmed:
        return "AWAITING_SAMPLE_APPROVAL"
    domains = {(urlsplit(s["root"]).hostname or "").removeprefix("www.") for s in sites}
    if len(sites) != 5 or len(domains) != 5 or "" in domains:
        return "NOT_PASSED"
    if any(not any(p["status"] == "available" and p["evidence"] for p in s["pages"])
           for s in sites):
        return "NOT_PASSED"
    return "PASS_WITH_LIMITATIONS"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", required=True)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--confirmed-sample", action="store_true")
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("artifacts/private/web"))
    args = parser.parse_args()
    if not args.live:
        print("Plan only: max 4 pages/site; no network; --live requires confirmed sample.")
        return 0
    if not args.confirmed_sample or len(args.url) != 5:
        parser.error("Live pilot requires five confirmed sample URLs.")
    output = args.output.resolve()
    probe = output / "report.json"
    ignored = subprocess.run(["git", "check-ignore", "-q", str(probe)], check=False)
    if ignored.returncode != 0:
        parser.error("Output must be ignored by Git.")
    output.mkdir(parents=True, exist_ok=False)
    sites = []
    for index, url in enumerate(args.url):
        crawler = WebsiteCrawler(url, output / f"site-{index+1}", browser=args.browser)
        try:
            site = crawler.crawl()
        finally:
            crawler.client.close()
        sites.append(site)
        # Persist after every site; raw and normalized records remain private.
        probe.write_text(json.dumps({"started_or_updated_at": datetime.now(UTC).isoformat(),
                                     "sites": sites}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"site": index + 1, "pages": len(site["pages"]),
                          "available": sum(p["status"] == "available" for p in site["pages"]),
                          "requests": site["requests"]}))
    report = {"gate_status": acceptance(sites, args.confirmed_sample),
              "test_date": datetime.now(UTC).isoformat(), "version": "gate1b-v1",
              "sample_confirmed": args.confirmed_sample, "sites": sites}
    probe.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report["gate_status"])
    return 0 if report["gate_status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
