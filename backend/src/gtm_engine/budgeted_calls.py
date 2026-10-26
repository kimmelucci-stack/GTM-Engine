"""One-shot provider boundary. No automatic retries, including uncertain outcomes."""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Never, Protocol
from uuid import UUID

from gtm_engine.domain.run_budget import RunBudgetError, amount
from gtm_engine.persistence.database import PersistenceUnavailable


@dataclass(frozen=True)
class CostRequest:
    budget_id: UUID
    run_id: UUID
    event_id: str
    provider: str
    endpoint: str
    component: str
    ceiling: Decimal


class Ledger(Protocol):
    def reserve(self, budget_id: UUID, run_id: UUID, event_id: str, *, provider: str,
                endpoint: str, component: str, ceiling: Decimal) -> None: ...
    def reconcile(self, budget_id: UUID, event_id: str, actual: Decimal) -> dict: ...
    def uncertain(self, budget_id: UUID, event_id: str) -> None: ...


class BudgetedCallError(Exception):
    def __init__(self, code: str, event_id: str, actual: Decimal | None = None):
        super().__init__(code)
        self.event_id = event_id
        self.actual = actual


@dataclass(frozen=True)
class BudgetedResult[T]:
    value: T
    budget: dict


def execute_budgeted[T](ledger: Ledger, request: CostRequest, call: Callable[[], T],
                     measure: Callable[[T], Decimal]) -> BudgetedResult[T]:
    # reserve() must return only after its transaction committed successfully.
    ledger.reserve(request.budget_id, request.run_id, request.event_id,
                   provider=request.provider, endpoint=request.endpoint,
                   component=request.component, ceiling=request.ceiling)

    def uncertain(code: str) -> Never:
        try:
            ledger.uncertain(request.budget_id, request.event_id)
        except (PersistenceUnavailable, RunBudgetError):
            # The committed reservation still exists; do not release it or repeat the call.
            pass
        raise BudgetedCallError(code, request.event_id) from None

    try:
        result = call()
    except Exception:  # noqa: BLE001 -- redact arbitrary provider errors at the boundary
        uncertain("provider_outcome_uncertain")
    try:
        actual = amount(measure(result))
    except Exception:  # noqa: BLE001 -- missing cost never becomes a zero charge
        uncertain("actual_cost_unavailable")
    try:
        summary = ledger.reconcile(request.budget_id, request.event_id, actual)
    except (PersistenceUnavailable, RunBudgetError):
        # Expose only safe accounting fields for later reconciliation, never the response.
        raise BudgetedCallError("cost_reconciliation_pending", request.event_id, actual) from None
    return BudgetedResult(result, summary)
