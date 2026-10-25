"""Bounded DataForSEO transport for Gate 1A. No automatic request retries."""

import base64
import re
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field, SecretStr

API_BASE = "https://api.dataforseo.com"
REVIEW_POST = "/v3/business_data/google/reviews/task_post"
REVIEW_GET = "/v3/business_data/google/reviews/task_get/"
PILOT_ENDPOINTS = {
    ("GET", "/v3/keywords_data/google_ads/locations/IT"),
    ("POST", "/v3/keywords_data/google_ads/search_volume/live"),
    ("POST", "/v3/dataforseo_labs/google/keyword_ideas/live"),
    ("POST", "/v3/dataforseo_labs/google/search_intent/live"),
    ("POST", "/v3/keywords_data/google_trends/explore/live"),
    ("POST", REVIEW_POST),
    *(("POST", f"/v3/serp/google/{kind}/live/advanced") for kind in
      ["autocomplete", "organic", "maps", "ads_advertisers", "ads_search"]),
}


def allowed_request(method: str, path: str) -> bool:
    return (method, path) in PILOT_ENDPOINTS or (
        method == "GET" and bool(re.fullmatch(re.escape(REVIEW_GET) + r"[a-fA-F0-9-]{36}", path))
    )


class ProviderError(Exception):
    """Safe code only: never expose a provider response or request headers."""


class BudgetError(ProviderError):
    pass


class Settings(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)
    login: SecretStr
    password: SecretStr
    cost_cap_usd: Decimal = Field(gt=0, allow_inf_nan=False)


class Budget:
    """Reserve conservative ceilings; failed/uncertain requests keep their reservation."""

    def __init__(self, cap: Decimal, max_requests: int = 20):
        if not cap.is_finite() or cap <= 0 or max_requests <= 0:
            raise BudgetError("invalid_budget")
        self.cap = cap
        self.max_requests = max_requests
        self.reserved = Decimal(0)
        self.observed = Decimal(0)
        self.requests = 0
        self.halted = False

    def reserve(self, ceiling: Decimal) -> None:
        if self.halted:
            raise BudgetError("budget_halted")
        if not ceiling.is_finite() or ceiling < 0:
            raise BudgetError("invalid_price_ceiling")
        if self.requests >= self.max_requests or self.reserved + ceiling > self.cap:
            raise BudgetError("budget_or_request_limit")
        self.reserved += ceiling
        self.requests += 1

    def reconcile(self, cost: Any, ceiling: Decimal) -> None:
        try:
            amount = Decimal(str(cost))
            if not amount.is_finite() or amount < 0:
                raise ValueError
        except (ValueError, ArithmeticError):
            self.halted = True
            raise BudgetError("cost_unknown_reconcile_before_continuing") from None
        self.observed += amount
        if amount > ceiling:
            self.halted = True
            raise BudgetError("price_ceiling_exceeded_reconcile_account")


def redact(value: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in {
                "authorization", "password", "login", "token", "api_key", "access_token"
            } else redact(item, secrets)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item, secrets) for item in value]
    if isinstance(value, str):
        for secret in sorted((s for s in secrets if s), key=len, reverse=True):
            value = value.replace(secret, "[REDACTED]")
    return value


class DataForSEO:
    def __init__(
        self,
        settings: Settings,
        budget: Budget,
        journal: Callable[[dict[str, Any]], None],
        transport: httpx.BaseTransport | None = None,
    ):
        self.budget = budget
        self.journal = journal
        login, password = settings.login.get_secret_value(), settings.password.get_secret_value()
        encoded = base64.b64encode(f"{login}:{password}".encode()).decode()
        self.secrets = (login, password, encoded)
        self.http = httpx.Client(
            base_url=API_BASE,
            auth=httpx.BasicAuth(login, password),
            timeout=httpx.Timeout(45),
            follow_redirects=False,
            trust_env=False,
            transport=transport,
        )

    def close(self) -> None:
        self.http.close()

    def request(
        self, method: str, path: str, payload: list[dict[str, Any]] | None, ceiling: Decimal
    ) -> dict[str, Any]:
        # Only the pilot allowlist may determine paths; no user-supplied host/URL.
        if not allowed_request(method, path):
            raise ProviderError("endpoint_not_allowed")
        self.budget.reserve(ceiling)
        event: dict[str, Any] = {
            "endpoint": path, "method": method, "input": payload,
            "observed_at": datetime.now(UTC).isoformat(),
            "reserved_usd": str(ceiling), "state": "reserved_before_send",
        }
        # Durable journal before sending. A crash leaves evidence of a possible charge.
        self.journal(redact(event, self.secrets))
        try:
            response = self.http.request(method, path, json=payload)
        except httpx.HTTPError:
            self.budget.halted = True
            raise ProviderError("transport_unknown_outcome_no_retry") from None
        event["http_status"] = response.status_code
        if response.status_code != 200:
            self.budget.halted = True
            event["state"] = "http_error_no_retry"
            self.journal(redact(event, self.secrets))
            raise ProviderError(f"http_{response.status_code}_no_retry")
        try:
            body = response.json()
            if not isinstance(body, dict):
                raise TypeError
            tasks = body.get("tasks")
            if tasks is not None and (
                not isinstance(tasks, list) or any(not isinstance(t, dict) for t in tasks)
            ):
                raise TypeError
        except (ValueError, TypeError):
            self.budget.halted = True
            raise ProviderError("invalid_json_unknown_cost_no_retry") from None
        safe_body = redact(body, self.secrets)
        event.update(state="response_received", response=safe_body)
        self.journal(redact(event, self.secrets))
        self.budget.reconcile(body.get("cost"), ceiling)
        return safe_body
