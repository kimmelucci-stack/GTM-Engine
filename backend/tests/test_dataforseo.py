"""Synthetic envelopes only. No live HTTP or customer fixtures in CI."""

import base64
import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import httpx
import pytest

from gtm_engine import gate1a
from gtm_engine.providers.dataforseo import (
    Budget,
    BudgetError,
    DataForSEO,
    ProviderError,
    Settings,
    redact,
)


def settings():
    return Settings(**dict(zip(
        ["login", "password", "cost_cap_usd"],
        ["synthetic-account", "synthetic-password", "5"], strict=True,
    )))


def envelope(result=None, status=20000, cost="0.01"):
    return {"status_code": 20000, "cost": cost,
            "tasks": [{"id": "00000000-0000-0000-0000-000000000000", "status_code": status,
                       "result": result or []}]}


def probe(name):
    return next(p for p in gate1a.plan() if p["id"] == name)


@pytest.mark.parametrize("cap", ["0", "-1", "NaN", "Infinity"])
def test_invalid_budget_never_allows_requests(cap):
    with pytest.raises(BudgetError):
        Budget(Decimal(cap))


def test_budget_reserves_before_request_and_does_not_refund():
    budget = Budget(Decimal("0.1"), max_requests=2)
    budget.reserve(Decimal("0.1"))
    budget.reconcile("0.01", Decimal("0.1"))
    with pytest.raises(BudgetError):
        budget.reserve(Decimal("0.01"))
    assert budget.observed == Decimal("0.01")
    assert budget.reserved == Decimal("0.1")


def test_request_limit_includes_zero_cost_gets():
    budget = Budget(Decimal(1), max_requests=1)
    budget.reserve(Decimal(0))
    with pytest.raises(BudgetError):
        budget.reserve(Decimal(0))


@pytest.mark.parametrize("cost", [None, "NaN", "-1", "Infinity", "invalid", "0.11"])
def test_unknown_or_excess_cost_stops_further_spending(cost):
    budget = Budget(Decimal(1))
    budget.reserve(Decimal("0.1"))
    with pytest.raises(BudgetError):
        budget.reconcile(cost, Decimal("0.1"))
    with pytest.raises(BudgetError):
        budget.reserve(Decimal(0))


def test_transport_redacts_credentials_even_when_provider_echoes_them():
    events = []
    config = settings()
    encoded = base64.b64encode(b"synthetic-account:synthetic-password").decode()
    body = envelope()
    body["message"] = "synthetic-account synthetic-password " + encoded
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    client = DataForSEO(config, Budget(Decimal(5)), events.append, transport)
    try:
        client.request("GET", probe("locations")["endpoint"], None, Decimal("0.1"))
    finally:
        client.close()
    serialized = json.dumps(events)
    assert "synthetic-account" not in serialized
    assert "synthetic-password" not in serialized
    assert encoded not in serialized
    assert events[0]["state"] == "reserved_before_send"


@pytest.mark.parametrize("status", [401, 429, 500, 302])
def test_http_errors_are_not_retried_or_exposed(status):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(status, text="private-provider-response")

    budget = Budget(Decimal(5))
    client = DataForSEO(settings(), budget, lambda event: None, httpx.MockTransport(respond))
    try:
        with pytest.raises(ProviderError) as error:
            client.request("POST", probe("ads")["endpoint"], probe("ads")["payload"], Decimal(1))
        assert "private-provider-response" not in str(error.value)
        assert len(calls) == 1 and budget.halted
    finally:
        client.close()


def test_timeout_never_reposts_paid_task():
    calls = []

    def timeout(request):
        calls.append(request)
        raise httpx.ReadTimeout("private exception", request=request)

    client = DataForSEO(settings(), Budget(Decimal(5)), lambda event: None,
                       httpx.MockTransport(timeout))
    try:
        with pytest.raises(ProviderError, match="unknown_outcome"):
            client.request("POST", gate1a.REVIEW_POST, [], Decimal(1))
        assert len(calls) == 1
    finally:
        client.close()


def test_external_host_rejected_before_credentials_can_be_sent():
    events = []
    client = DataForSEO(settings(), Budget(Decimal(5)), events.append,
                       httpx.MockTransport(lambda request: pytest.fail("network called")))
    try:
        with pytest.raises(ProviderError, match="not_allowed"):
            client.request("GET", "https://other.invalid/", None, Decimal(0))
        assert events == []
    finally:
        client.close()


def test_no_call_when_reservation_exceeds_cap():
    client = DataForSEO(settings(), Budget(Decimal("0.1")), lambda event: None,
                       httpx.MockTransport(lambda request: pytest.fail("network called")))
    try:
        with pytest.raises(BudgetError):
            client.request("GET", probe("locations")["endpoint"], None, Decimal(1))
    finally:
        client.close()


def test_empty_success_does_not_prove_absence():
    result = gate1a.assess(probe("ads"), envelope())
    assert result["availability"] == "unavailable"
    assert "empty_result_not_verified_absence" in result["limitations"]


def test_task_failure_is_not_successful_data():
    assert gate1a.assess(probe("ads"), envelope(status=40101))["availability"] == "unavailable"


@pytest.mark.parametrize("value,expected", [(None, "partial"), (0, "available")])
def test_missing_volume_and_verified_zero_remain_distinct(value, expected):
    result = gate1a.assess(probe("volume_city"), envelope([
        {"location_code": gate1a.CITY, "search_volume": value, "cpc": 0},
    ]))
    assert result["availability"] == expected


def test_national_response_is_not_presented_as_city_data():
    result = gate1a.assess(probe("volume_city"), envelope([
        {"location_code": gate1a.COUNTRY, "search_volume": 10, "cpc": 1},
    ]))
    assert result["availability"] == "partial"
    assert result["geo_requested"] == gate1a.CITY


def test_sparse_trends_series_is_partial_without_interpolation():
    values = [1, 2, 3] + [None] * 50  # Synthetic, reproduces the historic coverage failure shape.
    body = envelope([{"location_code": gate1a.COUNTRY, "items": [
        {"type": "google_trends_graph", "data": [{"values": [v]} for v in values]},
    ]}])
    report = gate1a.assess(probe("trends"), body)
    assert report["sample_count"] == 53 and report["non_null"] == 3
    assert report["availability"] == "partial"
    assert values.count(None) == 50


def test_paa_absence_is_explicit():
    report = gate1a.assess(probe("organic"), envelope([
        {"location_code": gate1a.CITY, "items": [{"type": "organic"}]},
    ]))
    assert report["paa_count"] == 0 and report["availability"] == "partial"


def test_plan_covers_twelve_historic_probes_and_country():
    assert len(gate1a.plan()) == 13
    assert {p["id"] for p in gate1a.plan()} >= {"volume_city", "volume_region", "volume_country"}
    assert probe("reviews")["payload"][0]["depth"] == 10
    assert probe("ads")["payload"][0]["depth"] == 40


def test_price_card_requires_exact_plan_currency_and_fresh_date(tmp_path):
    card = {"checked_at": datetime.now(UTC).isoformat(), "currency": "USD",
            "source_url": "https://dataforseo.com/pricing", "plan": gate1a.plan(),
            "ceilings_usd": {p["id"]: "0.1" for p in gate1a.plan()}}
    card["ceilings_usd"]["reviews_poll"] = "0"
    file = tmp_path / "rates.json"
    file.write_text(json.dumps(card))
    assert gate1a.load_prices(file, gate1a.plan())["ads"] == Decimal("0.1")
    card["checked_at"] = (datetime.now(UTC) - timedelta(days=8)).isoformat()
    file.write_text(json.dumps(card))
    with pytest.raises(ValueError):
        gate1a.load_prices(file, gate1a.plan())


def test_settings_and_recursive_redaction_do_not_reveal_values():
    assert "synthetic-password" not in repr(settings())
    output = redact({"nested": [{"authorization": "private", "text": "my-secret"}]},
                    ("my-secret",))
    assert "private" not in json.dumps(output) and "my-secret" not in json.dumps(output)


def test_failed_resume_cannot_overwrite_previous_budget(tmp_path):
    directory = tmp_path / "pilot"
    directory.mkdir()
    (directory / "report.json").write_text('{"checks":[]}')
    previous = '{"cap":"5","reserved":"4","observed":"4","requests":15,"halted":false}'
    (directory / "budget.json").write_text(previous)
    with pytest.raises(ProviderError):
        gate1a.execute(settings(), {}, directory, resume_reviews=True)
    assert (directory / "budget.json").read_text() == previous
    assert not (directory / "run.lock").exists()


def test_settings_json_quoted_local_values_are_private(tmp_path, monkeypatch):
    monkeypatch.setattr(gate1a, "ROOT", tmp_path)
    for name in ["DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD", "DATAFORSEO_COST_CAP_USD"]:
        monkeypatch.delenv(name, raising=False)
    (tmp_path / ".env").write_text("\n".join(
        key + "=" + json.dumps(value) for key, value in zip(
            ["DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD", "DATAFORSEO_COST_CAP_USD"],
            ["synthetic-account", "synthetic-password", "5"], strict=True,
        )
    ))

    class Outcome:
        def __init__(self, code):
            self.returncode = code

    monkeypatch.setattr(gate1a.subprocess, "run", lambda args, **kwargs:
                        Outcome(0 if args[1] == "check-ignore" else 1))
    loaded, missing = gate1a.settings_from_environment()
    assert not missing and loaded.cost_cap_usd == Decimal(5)
    assert "synthetic-password" not in repr(loaded)


def test_settings_refuse_tracked_env(tmp_path, monkeypatch):
    monkeypatch.setattr(gate1a, "ROOT", tmp_path)
    (tmp_path / ".env").write_text("")

    class Tracked:
        returncode = 0

    monkeypatch.setattr(gate1a.subprocess, "run", lambda *args, **kwargs: Tracked())
    loaded, missing = gate1a.settings_from_environment()
    assert loaded is None and missing == ["local_env_not_protected"]


def test_resume_polls_saved_task_without_posting_or_resetting_budget(tmp_path, monkeypatch):
    directory = tmp_path / "pilot"
    directory.mkdir()
    saved = {"checks": [], "review_task_id": "00000000-0000-0000-0000-000000000000"}
    (directory / "report.json").write_text(json.dumps(saved))
    (directory / "budget.json").write_text(json.dumps(
        {"cap": "5", "reserved": "4", "observed": "3", "requests": 10, "halted": False}
    ))
    calls = []

    def request(self, method, path, payload, ceiling):
        self.budget.reserve(ceiling)
        calls.append((method, path))
        return envelope([{"location_code": gate1a.CITY, "items": [
            {"timestamp": "2026-01-01", "rating": {"value": 4}},
        ]}])

    monkeypatch.setattr(DataForSEO, "request", request)
    result = gate1a.execute(settings(), {"reviews_poll": Decimal(0)}, directory,
                           resume_reviews=True)
    assert len(calls) == 1 and calls[0][0] == "GET"
    assert result["cost_reserved_usd"] == "4" and result["request_count"] == 11


def test_pilot_cannot_exceed_authorized_five_dollars(tmp_path):
    config = settings().model_copy(update={"cost_cap_usd": Decimal(6)})
    with pytest.raises(ProviderError, match="authorized_pilot"):
        gate1a.execute(config, {}, tmp_path / "pilot")


def test_reviews_can_start_once_using_saved_maps_identity(tmp_path, monkeypatch):
    directory = tmp_path / "pilot"
    directory.mkdir()
    (directory / "report.json").write_text(json.dumps({
        "checks": [{"probe": "reviews", "availability": "unavailable"}],
        "review_candidates": [{"place_id": "synthetic-place", "title": "Synthetic company"}],
    }))
    (directory / "budget.json").write_text(json.dumps(
        {"cap": "5", "reserved": "1", "observed": "0.5", "requests": 12, "halted": False}
    ))
    calls = []

    def request(self, method, path, payload, ceiling):
        self.budget.reserve(ceiling)
        calls.append(method)
        if method == "POST":
            assert payload[0]["place_id"] == "synthetic-place"
            return envelope(status=20100)
        return envelope([{"location_code": gate1a.CITY, "items": []}])

    monkeypatch.setattr(DataForSEO, "request", request)
    monkeypatch.setattr(gate1a.time, "sleep", lambda seconds: None)
    prices = {"reviews": Decimal("0.1"), "reviews_poll": Decimal(0)}
    gate1a.execute(settings(), prices, directory, "synthetic-place", start_reviews=True)
    assert calls.count("POST") == 1
    before = (directory / "budget.json").read_text()
    with pytest.raises(ProviderError):
        gate1a.execute(settings(), prices, directory, "synthetic-place", start_reviews=True)
    assert (directory / "budget.json").read_text() == before
