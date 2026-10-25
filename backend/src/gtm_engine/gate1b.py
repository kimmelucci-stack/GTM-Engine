"""Opt-in private competitor crawl. No API credentials are read."""

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from gtm_engine.providers.web import WebsiteCrawler


def target_domains(urls: list[str]) -> set[str]:
    return {(urlsplit(url).hostname or "").removeprefix("www.") for url in urls}


def validate_mode(urls: list[str], *, screen: bool, confirmed: bool, browser: bool) -> None:
    domains = target_domains(urls)
    if "" in domains or len(domains) != len(urls):
        raise ValueError("Provide distinct website domains; deduplicate shared candidates first")
    if screen:
        if confirmed or browser:
            raise ValueError("Screening is HTTP-only and does not approve a competitor sample")
        if not 1 <= len(urls) <= 16:
            raise ValueError("Screening requires 1..16 distinct websites")
    elif not confirmed or len(urls) != 5:
        raise ValueError("Detailed live pilot requires five confirmed sample URLs")


def screening_summary(sites: list[dict]) -> dict:
    available = sum(any(p["status"] == "available" and p["evidence"] for p in site["pages"])
                    for site in sites)
    return {"gate_status": "AWAITING_SAMPLE_APPROVAL", "sample_confirmed": False,
            "mode": "screening", "websites_checked": len(sites),
            "websites_with_evidence": available,
            "screening_status": "completed" if available == len(sites) else "partial",
            "limitations": ["One offer page per website; not a detailed competitor profile.",
                            "Website access does not establish commercial fit or search rank.",
                            "Owner confirmation still required before detailed collection."]}


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
    parser.add_argument("--screen", action="store_true",
                        help="Light HTTP screening only: one page/site, no sample approval")
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("artifacts/private/web"))
    args = parser.parse_args()
    if not args.live:
        if args.screen:
            print("Screening plan: one page/site, max 16 sites, 10 requests/site; no network.")
        else:
            print("Plan only: max 4 pages/site; no network; --live requires confirmed sample.")
        return 0
    try:
        validate_mode(args.url, screen=args.screen, confirmed=args.confirmed_sample,
                      browser=args.browser)
    except ValueError as error:
        parser.error(str(error))
    output = args.output.resolve()
    probe = output / "report.json"
    ignored = subprocess.run(["git", "check-ignore", "-q", str(probe)], check=False)
    if ignored.returncode != 0:
        parser.error("Output must be ignored by Git.")
    output.mkdir(parents=True, exist_ok=False)
    sites = []
    for index, url in enumerate(args.url):
        crawler = WebsiteCrawler(url, output / f"site-{index+1}", browser=args.browser,
                                 max_pages=1 if args.screen else 4,
                                 max_requests=10 if args.screen else None)
        try:
            site = crawler.crawl()
        finally:
            crawler.client.close()
        sites.append(site)
        # Persist after every site; raw and normalized records remain private.
        probe.write_text(json.dumps({"mode": "screening" if args.screen else "detailed",
                                     "execution_status": "in_progress",
                                     "started_or_updated_at": datetime.now(UTC).isoformat(),
                                     "sites": sites}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"site": index + 1, "pages": len(site["pages"]),
                          "available": sum(p["status"] == "available" for p in site["pages"]),
                          "requests": site["requests"]}))
    report = {"gate_status": acceptance(sites, args.confirmed_sample),
              "mode": "detailed", "execution_status": "completed",
              "test_date": datetime.now(UTC).isoformat(),
              "version": "gate1b-screen-v1" if args.screen else "gate1b-v1",
              "sample_confirmed": args.confirmed_sample, "sites": sites}
    if args.screen:
        report.update(screening_summary(sites))
    probe.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(report["gate_status"])
    if args.screen:
        return 0 if report["websites_with_evidence"] else 1
    return 0 if report["gate_status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
