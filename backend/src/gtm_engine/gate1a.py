"""Reproducible, opt-in pilot. Raw results stay in ignored private artifacts."""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from gtm_engine.providers.dataforseo import (
    REVIEW_GET,
    REVIEW_POST,
    Budget,
    DataForSEO,
    ProviderError,
    Settings,
)

ROOT = Path(__file__).resolve().parents[3]
PRIVATE = ROOT / "artifacts" / "private" / "dataforseo"
KEYWORD = "team building aziendale"
CITY, REGION, COUNTRY = 1008857, 9053436, 2380


def plan() -> list[dict[str, Any]]:
    rows = [{"id": "locations", "method": "GET",
             "endpoint": "/v3/keywords_data/google_ads/locations/IT", "payload": None}]
    for name, code in [("city", CITY), ("region", REGION), ("country", COUNTRY)]:
        rows.append({"id": f"volume_{name}", "method": "POST",
                     "endpoint": "/v3/keywords_data/google_ads/search_volume/live",
                     "payload": [{"keywords": [KEYWORD], "location_code": code,
                                  "language_code": "it"}]})
    rows.extend([
        {"id": "ideas", "method": "POST",
         "endpoint": "/v3/dataforseo_labs/google/keyword_ideas/live",
         "payload": [{"keywords": [KEYWORD], "location_code": COUNTRY,
                      "language_code": "it", "limit": 5}]},
        {"id": "intent", "method": "POST",
         "endpoint": "/v3/dataforseo_labs/google/search_intent/live",
         "payload": [{"keywords": [KEYWORD]}]},
    ])
    for name, kind, query in [
        ("autocomplete", "autocomplete", KEYWORD),
        ("organic", "organic", KEYWORD + " torino"),
        ("maps", "maps", KEYWORD + " torino"),
    ]:
        payload = {"keyword": query, "location_code": CITY, "language_code": "it"}
        if kind != "autocomplete":
            payload["depth"] = 10
        rows.append({"id": name, "method": "POST",
                     "endpoint": f"/v3/serp/google/{kind}/live/advanced", "payload": [payload]})
    rows.extend([
        {"id": "trends", "method": "POST",
         "endpoint": "/v3/keywords_data/google_trends/explore/live",
         "payload": [{"keywords": [KEYWORD], "location_code": COUNTRY,
                      "language_code": "it", "time_range": "past_12_months", "type": "web"}]},
        {"id": "advertisers", "method": "POST",
         "endpoint": "/v3/serp/google/ads_advertisers/live/advanced",
         "payload": [{"keyword": "team building", "location_code": COUNTRY}]},
        {"id": "ads", "method": "POST",
         "endpoint": "/v3/serp/google/ads_search/live/advanced",
         "payload": [{"target": "madeinteam.it", "location_code": COUNTRY, "depth": 40}]},
        {"id": "reviews", "method": "POST", "endpoint": REVIEW_POST,
         "payload": [{"place_id": "FROM_VERIFIED_MAPS_RESULT", "location_code": CITY,
                      "language_code": "it", "depth": 10}]},
    ])
    return rows


def settings_from_environment() -> tuple[Settings | None, list[str]]:
    names = ["DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD", "DATAFORSEO_COST_CAP_USD"]
    values = {}
    env_file = ROOT / ".env"
    if env_file.exists():
        check = subprocess.run(
            ["git", "check-ignore", "-q", ".env"], cwd=ROOT, capture_output=True, check=False
        )
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", ".env"], cwd=ROOT, capture_output=True, check=False
        )
        if check.returncode != 0 or tracked.returncode == 0:
            return None, ["local_env_not_protected"]
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() in names:
                raw = value.strip()
                if raw.startswith('"'):
                    values[key.strip()] = json.loads(raw)
                elif len(raw) >= 2 and raw[0] == raw[-1] == "'":
                    values[key.strip()] = raw[1:-1]
                else:
                    values[key.strip()] = raw
    for name in names:
        if os.environ.get(name):
            values[name] = os.environ[name]
    missing = [name for name in names if not values.get(name)]
    if missing:
        return None, missing
    try:
        return Settings(login=values[names[0]], password=values[names[1]],
                        cost_cap_usd=values[names[2]]), []
    except ValueError:
        return None, ["invalid_settings_values_withheld"]


def result_rows(body: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for task in body.get("tasks") or [] for r in task.get("result") or []
            if isinstance(r, dict)]


def assess(probe: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    """Coverage of the sample, never statistical confidence or strategic validation."""
    tasks = body.get("tasks") or []
    codes = [task.get("status_code") for task in tasks]
    report: dict[str, Any] = {
        "probe": probe["id"], "provider_status": body.get("status_code"),
        "task_statuses": codes, "availability": "unavailable", "sample_count": 0,
        "limitations": [],
    }
    if body.get("status_code") != 20000 or not tasks or any(code != 20000 for code in codes):
        report["limitations"] = ["provider_or_task_not_successful"]
        return report
    results = result_rows(body)
    name = probe["id"]
    items = [item for row in results for item in row.get("items") or []
             if isinstance(item, dict)]
    records = results if name.startswith("volume_") or name == "locations" else items
    report["sample_count"] = len(records)
    if not records:
        report["limitations"] = ["empty_result_not_verified_absence"]
        return report
    report["availability"] = "available"
    if name == "locations":
        codes_found = {row.get("location_code") for row in records}
        if CITY not in codes_found:
            report.update(availability="partial", limitations=["pilot_city_not_in_catalog"])
    elif name.startswith("volume_"):
        requested = probe["payload"][0]["location_code"]
        effective = {row.get("location_code") for row in results}
        report.update(geo_requested=requested, geo_effective=list(effective))
        if effective != {requested}:
            report.update(availability="partial", limitations=["geography_mismatch_or_missing"])
        if not any(row.get("search_volume") is not None for row in results):
            report["availability"] = "partial"
            report["limitations"].append("volume_missing_not_zero")
        if not any(row.get("cpc") is not None for row in results):
            report["limitations"].append("cpc_missing")
            report["availability"] = "partial"
    elif name == "trends":
        points = [point for item in items if item.get("type") == "google_trends_graph"
                  for point in item.get("data") or []]
        values = [v for point in points for v in point.get("values") or []]
        report.update(sample_count=len(values), non_null=sum(v is not None for v in values))
        report["availability"] = "available" if values and all(v is not None for v in values) \
            else "partial" if values else "unavailable"
        report["limitations"] = ["relative_index_not_search_volume"]
        if not values or any(v is None for v in values):
            report["limitations"].append("incomplete_series_no_interpolation")
    elif name == "organic":
        report["paa_count"] = sum(i.get("type") == "people_also_ask" for i in items)
        report["organic_count"] = sum(i.get("type") == "organic" for i in items)
        if not report["paa_count"]:
            report.update(availability="partial", limitations=["paa_not_observed_in_sample"])
    elif name == "reviews":
        if len(items) < 10:
            report.update(availability="partial", limitations=["fewer_than_ten_reviews"])
        if any(not item.get("timestamp") or not item.get("rating") for item in items):
            report["availability"] = "partial"
            report["limitations"].append("review_dates_or_rating_missing")
    elif name == "intent":
        if any(not isinstance(item.get("keyword_intent"), dict)
               or item["keyword_intent"].get("probability") is None for item in items):
            report.update(availability="partial", limitations=["intent_probability_missing"])
        report["limitations"].append("model_classification_not_observed_buyer_intent")
    elif name == "ads":
        if any(not item.get("creative_id") or not item.get("advertiser_id") for item in items):
            report.update(availability="partial", limitations=["ad_identifiers_missing"])
    if name not in {"locations", "intent"} and not name.startswith("volume_"):
        requested = probe["payload"][0].get("location_code")
        effective = [row.get("location_code") for row in results]
        report.update(geo_requested=requested, geo_effective=effective)
        if not effective or any(code != requested for code in effective):
            report["availability"] = "partial"
            report["limitations"].append("geography_mismatch_or_missing")
    return report


def load_prices(path: Path, probes: list[dict[str, Any]]) -> dict[str, Decimal]:
    """No invented tariff: ceilings must be reviewed for this exact pilot beforehand."""
    data = json.loads(path.read_text(encoding="utf-8"))
    checked = datetime.fromisoformat(data["checked_at"])
    if checked.tzinfo is None:
        raise ValueError("rate_card_requires_timezone")
    age = datetime.now(UTC) - checked
    if checked.tzinfo is None or age < timedelta(0) or age > timedelta(days=7):
        raise ValueError("rate_card_stale_or_undated")
    if data.get("currency") != "USD" or data.get("plan") != plan():
        raise ValueError("rate_card_plan_or_currency_mismatch")
    prices = {row["id"]: Decimal(str(data["ceilings_usd"][row["id"]])) for row in probes}
    prices["reviews_poll"] = Decimal(str(data["ceilings_usd"]["reviews_poll"]))
    if any(not value.is_finite() or value < 0 for value in prices.values()):
        raise ValueError("invalid_price")
    if not str(data.get("source_url", "")).startswith("https://dataforseo.com/"):
        raise ValueError("official_pricing_source_required")
    return prices


def execute(
    settings: Settings, prices: dict[str, Decimal], directory: Path,
    review_place_id: str | None = None, resume_reviews: bool = False, start_reviews: bool = False,
) -> dict[str, Any]:
    if settings.cost_cap_usd > Decimal(5):
        raise ProviderError("cap_exceeds_authorized_pilot_limit")
    # Exclusive new directory prevents overwriting previous evidence or silently rerunning it.
    directory.mkdir(parents=True, exist_ok=resume_reviews or start_reviews, mode=0o700)
    lock = directory / "run.lock"
    try:
        lock_fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ProviderError("pilot_locked_reconcile_previous_run") from None
    os.close(lock_fd)
    budget = Budget(settings.cost_cap_usd)
    journal_path = directory / "journal.jsonl"
    budget_path = directory / "budget.json"
    report: dict[str, Any] = {"gate": "1A", "status": "partial", "checks": []}
    task_id = None
    if resume_reviews or start_reviews:
        try:
            report = json.loads((directory / "report.json").read_text(encoding="utf-8"))
            state = json.loads(budget_path.read_text(encoding="utf-8"))
            if Decimal(state["cap"]) != settings.cost_cap_usd or state["halted"]:
                raise ProviderError("pilot_budget_requires_manual_reconciliation")
            task_id = report.get("review_task_id")
            if resume_reviews and not task_id:
                raise ProviderError("no_saved_review_task_to_resume")
            if start_reviews and (task_id or not review_place_id or review_place_id not in {
                item["place_id"] for item in report.get("review_candidates", [])
            }):
                raise ProviderError("review_identity_or_saved_task_requires_review")
            budget.reserved, budget.observed = Decimal(state["reserved"]), Decimal(state["observed"])
            budget.requests = state["requests"]
        except (OSError, ValueError, KeyError, ProviderError):
            lock.unlink()
            raise ProviderError("pilot_state_requires_reconciliation") from None

    def save_budget() -> None:
        state = {"cap": str(budget.cap), "reserved": str(budget.reserved),
                 "observed": str(budget.observed), "requests": budget.requests,
                 "halted": budget.halted}
        with budget_path.open("w", encoding="utf-8") as stream:
            json.dump(state, stream)
            stream.flush()
            os.fsync(stream.fileno())

    def journal(event: dict[str, Any]) -> None:
        save_budget()
        with journal_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    client = DataForSEO(settings, budget, journal)
    place_id = review_place_id if start_reviews else None
    try:
        if resume_reviews:
            assert task_id is not None
            report.pop("stop_code", None)
            review_probe = next(p for p in plan() if p["id"] == "reviews")
            report["checks"] = [r for r in report["checks"] if r["probe"] != "reviews"]
            for _ in range(5):
                body = client.request("GET", REVIEW_GET + task_id, None, prices["reviews_poll"])
                codes = [t.get("status_code") for t in body.get("tasks") or []]
                if codes and all(code == 20000 for code in codes):
                    break
                time.sleep(5)
            report["checks"].append(assess(review_probe, body))
            return report
        probes = plan()
        if start_reviews:
            report["checks"] = [r for r in report["checks"] if r["probe"] != "reviews"]
            report.pop("stop_code", None)
            probes = [probe for probe in probes if probe["id"] == "reviews"]
        for probe in probes:
            if probe["id"] == "reviews":
                if not place_id:
                    report["checks"].append({"probe": "reviews", "availability": "unavailable",
                                             "limitations": ["no_verified_place_id_from_maps"]})
                    continue
                probe["payload"][0]["place_id"] = place_id
            body = client.request(probe["method"], probe["endpoint"], probe["payload"],
                                  prices[probe["id"]])
            if probe["id"] == "maps":
                candidates = [item for row in result_rows(body) for item in row.get("items") or []
                              if item.get("place_id")]
                # Store candidates but never guess a business identity for review collection.
                report["review_candidates"] = [
                    {"place_id": item["place_id"], "title": item.get("title")}
                    for item in candidates
                ]
                # Only a preselected identity actually observed in Maps can incur review spend.
                place_id = next((item["place_id"] for item in candidates
                                 if item["place_id"] == review_place_id), None)
            if probe["id"] == "reviews":
                task = (body.get("tasks") or [{}])[0]
                if task.get("status_code") == 20100 and task.get("id"):
                    task_id = task["id"]
                    report["review_task_id"] = task_id
                    for _ in range(5):
                        time.sleep(5)
                        body = client.request("GET", REVIEW_GET + task_id, None,
                                              prices["reviews_poll"])
                        codes = [t.get("status_code") for t in body.get("tasks") or []]
                        if codes and all(code == 20000 for code in codes):
                            break
            check = assess(probe, body)
            check.update(endpoint=probe["endpoint"], test_input=probe["payload"],
                         observed_at=datetime.now(UTC).isoformat(),
                         raw_fixture_ref="journal.jsonl",
                         period_requested=(probe["payload"][0].get("time_range")
                                           if probe["payload"] else None))
            report["checks"].append(check)
    except ProviderError as error:
        report["stop_code"] = str(error)
    finally:
        client.close()
        save_budget()
        report["status"] = "pass" if (
            len(report["checks"]) == len(plan())
            and all(c["availability"] == "available" for c in report["checks"])
            and not report.get("stop_code")
        ) else "partial"
        report.update(cost_observed_usd=str(budget.observed),
                      cost_reserved_usd=str(budget.reserved), request_count=budget.requests,
                      raw_fixture_ref="journal.jsonl", version="0.1.0",
                      checked_at=datetime.now(UTC).isoformat())
        (directory / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        lock.unlink()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="Print public sample requests; no network")
    parser.add_argument("--live", action="store_true", help="Explicit opt-in to paid requests")
    parser.add_argument("--rate-card", type=Path)
    parser.add_argument("--review-place-id", help="Preverified public identity, must match Maps")
    parser.add_argument("--resume-reviews", action="store_true", help="GET saved task, never POST again")
    parser.add_argument("--start-reviews", action="store_true",
                        help="POST reviews once for a selected identity in saved Maps candidates")
    args = parser.parse_args()
    if args.plan:
        print(json.dumps(plan(), indent=2, ensure_ascii=False))
        return 0
    if args.resume_reviews and args.start_reviews:
        parser.error("Choose start or resume, never both")
    try:
        settings, missing = settings_from_environment()
    except (OSError, ValueError, TypeError):
        print('{"status":"gated","reason":"invalid_local_settings_values_withheld"}')
        return 2
    if missing:
        print(json.dumps({"status": "gated", "missing": missing, "values": "withheld"}))
        return 2
    if not args.live:
        print('{"status":"preflight_ready","network_calls":0}')
        return 0
    if not args.rate_card:
        print('{"status":"gated","reason":"reviewed_rate_card_required"}')
        return 2
    try:
        prices = load_prices(args.rate_card, plan())
    except (ValueError, KeyError, OSError, TypeError):
        print('{"status":"gated","reason":"invalid_rate_card_values_withheld"}')
        return 2
    assert settings is not None
    # Reserve for the complete plan plus bounded review polling before any request.
    if sum(prices.values()) + 4 * prices["reviews_poll"] > settings.cost_cap_usd:
        print('{"status":"gated","reason":"plan_exceeds_cap"}')
        return 2
    try:
        report = execute(settings, prices, PRIVATE / "pilot", args.review_place_id,
                         args.resume_reviews, args.start_reviews)
    except (ProviderError, OSError, ValueError, KeyError):
        print('{"status":"gated","reason":"pilot_state_requires_review_values_withheld"}')
        return 2
    print(json.dumps({"gate": "1A", "status": report["status"],
                      "request_count": report["request_count"], "raw": "private_only"}))
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
