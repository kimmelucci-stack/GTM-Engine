"""Durable shared budget. Commit before any provider call; no network work while locked."""

from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal
from uuid import UUID

import psycopg

from gtm_engine.domain.run_budget import RunBudget, RunBudgetError
from gtm_engine.persistence.database import connection

COMPONENTS = frozenset({"data", "ai", "execution", "allocated_fixed"})


class PostgresBudget:
    def create(self, owner_id: UUID, project_id: UUID, cap_usd: Decimal,
               max_requests: int = 100) -> UUID:
        RunBudget(cap_usd, max_requests=max_requests)
        if max_requests > 10000:
            raise RunBudgetError("invalid_run_limits")
        with connection("gtm_api", owner_id) as conn:
            row = conn.execute(
                "insert into gtm.budgets(project_id,cap_usd,max_requests) values(%s,%s,%s) returning id",
                (project_id, cap_usd, max_requests),
            ).fetchone()
        return row["id"]

    @contextmanager
    def _locked(self, budget_id: UUID) -> Iterator[tuple[psycopg.Connection, RunBudget, dict]]:
        with connection("gtm_worker") as conn:
            conn.execute("set local lock_timeout = '3s'")
            row = conn.execute("select * from gtm.budgets where id=%s for update",
                               (budget_id,)).fetchone()
            if row is None:
                raise RunBudgetError("unknown_budget")
            ledger = RunBudget(row["cap_usd"], max_requests=row["max_requests"])
            ledger.halted = row["halted"]
            ledger.unmeasured = set(row["unmeasured"])
            events = conn.execute("select * from gtm.cost_events where budget_id=%s order by created_at,event_id",
                                  (budget_id,)).fetchall()
            metadata = {}
            for event in events:
                ledger.events[event["event_id"]] = {
                    "provider": event["provider"], "component": event["component"],
                    "ceiling": event["ceiling_usd"], "actual": event["actual_usd"],
                    "status": event["status"],
                }
                metadata[event["event_id"]] = (event["run_id"], event["endpoint"])
            yield conn, ledger, metadata
            conn.execute("update gtm.budgets set halted=halted or %s,unmeasured=%s where id=%s",
                         (ledger.halted, sorted(ledger.unmeasured), budget_id))

    def reserve(self, budget_id: UUID, run_id: UUID, event_id: str, *, provider: str,
                endpoint: str, component: str, ceiling: Decimal) -> None:
        if (component not in COMPONENTS or not endpoint.strip() or len(endpoint) > 512
                or not 0 < len(event_id) <= 128 or not 0 < len(provider) <= 80):
            raise RunBudgetError("invalid_cost_identity")
        with self._locked(budget_id) as (conn, ledger, metadata):
            if event_id in metadata and metadata[event_id] != (run_id, endpoint):
                raise RunBudgetError("conflicting_cost_identity")
            ledger.reserve(event_id, provider=provider, component=component, ceiling=ceiling)
            # Composite FK enforces that this module run belongs to this budget/project.
            conn.execute("""insert into gtm.cost_events
                (budget_id,event_id,run_id,provider,endpoint,component,ceiling_usd,status)
                values(%s,%s,%s,%s,%s,%s,%s,'reserved')""",
                         (budget_id, event_id, run_id, provider, endpoint, component, ceiling))

    def reconcile(self, budget_id: UUID, event_id: str, actual: Decimal) -> dict:
        with self._locked(budget_id) as (conn, ledger, _):
            ledger.reconcile(event_id, actual)
            conn.execute("""update gtm.cost_events set actual_usd=%s,status=%s,
                settled_at=coalesce(settled_at,clock_timestamp()) where budget_id=%s and event_id=%s""",
                         (actual, ledger.events[event_id]["status"], budget_id, event_id))
            summary = ledger.summary()
        return summary

    def uncertain(self, budget_id: UUID, event_id: str) -> None:
        with self._locked(budget_id) as (conn, ledger, _):
            ledger.uncertain(event_id)
            conn.execute("update gtm.cost_events set status='uncertain' where budget_id=%s and event_id=%s",
                         (budget_id, event_id))

    def mark_unmeasured(self, budget_id: UUID, component: str) -> None:
        if component not in COMPONENTS:
            raise RunBudgetError("invalid_cost_component")
        with self._locked(budget_id) as (_, ledger, _metadata):
            ledger.mark_unmeasured(component)

    def summary(self, budget_id: UUID) -> dict:
        with self._locked(budget_id) as (_, ledger, _metadata):
            summary = ledger.summary()
        return summary
