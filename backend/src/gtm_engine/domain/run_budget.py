"""Cross-provider budget accounting. Pure domain layer; caller must persist atomically."""

from decimal import Decimal


class RunBudgetError(Exception):
    """Fixed safe error codes only."""


def amount(value: Decimal) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
        raise RunBudgetError("invalid_usd_amount")
    return value


class RunBudget:
    """One ledger per GTM run, across API, AI, compute and attributed fixed costs.

    No credentials, API calls or implicit spend authorization. Not thread-safe or
    durable: PostgreSQL transaction/locking and adapter integration still required.
    """

    def __init__(self, cap_usd: Decimal, *, max_requests: int = 100):
        self.cap = amount(cap_usd)
        if self.cap <= 0 or self.cap > Decimal(15) or max_requests < 1:
            raise RunBudgetError("invalid_run_limits")
        self.max_requests = max_requests
        self.events: dict[str, dict] = {}
        self.unmeasured: set[str] = set()
        self.required_components = {"data", "ai", "execution", "allocated_fixed"}
        self.halted = False

    @property
    def committed(self) -> Decimal:
        return sum((e["actual"] if e["actual"] is not None else e["ceiling"]
                    for e in self.events.values()), Decimal(0))

    @property
    def observed(self) -> Decimal:
        return sum((e["actual"] for e in self.events.values() if e["actual"] is not None), Decimal(0))

    def reserve(self, event_id: str, *, provider: str, component: str, ceiling: Decimal) -> None:
        ceiling = amount(ceiling)
        if not event_id.strip() or not provider.strip() or not component.strip():
            raise RunBudgetError("missing_cost_identity")
        if event_id in self.events:
            event = self.events[event_id]
            if (event["provider"], event["component"], event["ceiling"]) != (provider, component, ceiling):
                raise RunBudgetError("conflicting_cost_identity")
            # Never use an idempotent reservation as permission to repeat a paid request.
            raise RunBudgetError("event_already_reserved_reconcile_before_retry")
        if self.halted:
            raise RunBudgetError("run_budget_halted")
        if len(self.events) >= self.max_requests or self.committed + ceiling > self.cap:
            raise RunBudgetError("run_budget_or_request_limit")
        self.events[event_id] = {"provider": provider, "component": component, "ceiling": ceiling,
                                 "actual": None, "status": "reserved"}

    def reconcile(self, event_id: str, actual: Decimal) -> None:
        actual = amount(actual)
        if event_id not in self.events:
            raise RunBudgetError("unknown_cost_event")
        event = self.events[event_id]
        if event["actual"] is not None:
            if event["actual"] != actual:
                raise RunBudgetError("conflicting_actual_cost")
            return
        event.update(actual=actual, status="settled")
        if actual > event["ceiling"] or self.committed > self.cap:
            # Retain the actual spend before halting: never erase a cost overrun.
            self.halted = True
            event["status"] = "overrun"

    def uncertain(self, event_id: str) -> None:
        if event_id not in self.events or self.events[event_id]["actual"] is not None:
            raise RunBudgetError("invalid_uncertain_event")
        self.events[event_id]["status"] = "uncertain"

    def mark_unmeasured(self, component: str) -> None:
        if not component.strip():
            raise RunBudgetError("missing_cost_component")
        self.unmeasured.add(component)

    def summary(self) -> dict:
        pending = [key for key, e in self.events.items() if e["actual"] is None]
        measured = {e["component"] for e in self.events.values() if e["actual"] is not None}
        missing = sorted(self.required_components - measured)
        return {"currency": "USD", "target_usd": "10", "cap_usd": str(self.cap),
                "target_exceeded": self.observed > Decimal(10), "observed_usd": str(self.observed),
                "committed_usd": str(self.committed), "remaining_usd": str(max(Decimal(0),
                                                                            self.cap-self.committed)),
                "pending_event_ids": pending, "unmeasured_components": sorted(self.unmeasured),
                "missing_required_components": missing,
                "halted": self.halted,
                "fully_reconciled": bool(self.events) and not pending and not self.unmeasured and not missing,
                "budget_compliance_proven": bool(self.events) and not pending and not self.unmeasured
                and not missing and not self.halted and self.observed <= self.cap}
