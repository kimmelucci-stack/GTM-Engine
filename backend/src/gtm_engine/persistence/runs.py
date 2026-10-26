"""Atomic owner-authorized foundation enqueue; no arbitrary provider tasks."""

from decimal import Decimal
from uuid import UUID

from gtm_engine.persistence.database import connection

OPERATIONS = frozenset({"catalog.validate", "catalog.archive"})
RUN_FIELDS = "id,project_id,module_no,mode,status,budget_id,cost_cap,created_at,started_at,completed_at"


class RunError(Exception):
    pass


def enqueue(owner_id: UUID, project_id: UUID, request_id: UUID, operation: str,
            cap_usd: Decimal) -> tuple[dict, bool]:
    if operation not in OPERATIONS or not cap_usd.is_finite() or not 0 < cap_usd <= 15:
        raise RunError("invalid_run_request")
    with connection("gtm_api", owner_id) as conn:
        conn.execute("set local lock_timeout = '3s'")
        if conn.execute("select id from gtm.projects where id=%s", (project_id,)).fetchone() is None:
            raise RunError("not_found")
        # Same project requests serialize; unique constraint independently prevents duplicates.
        conn.execute("select pg_advisory_xact_lock(hashtextextended(%s,0))", (str(project_id),))
        existing = conn.execute(f"select {RUN_FIELDS} from gtm.runs where project_id=%s and request_id=%s",
                                (project_id, request_id)).fetchone()
        if existing:
            if existing["mode"] != "foundation:" + operation or existing["cost_cap"] != cap_usd:
                raise RunError("idempotency_conflict")
            return existing, False
        budget = conn.execute("""insert into gtm.budgets(project_id,cap_usd)
            values(%s,%s) returning id""", (project_id, cap_usd)).fetchone()
        run = conn.execute(f"""insert into gtm.runs
            (project_id,module_no,mode,cost_cap,budget_id,request_id)
            values(%s,1,%s,%s,%s,%s) returning {RUN_FIELDS}""",
                           (project_id, "foundation:" + operation, cap_usd, budget["id"], request_id)
                           ).fetchone()
        conn.execute("insert into gtm.jobs(run_id,task_type,max_attempts) values(%s,%s,%s)",
                     (run["id"], operation, 3 if operation == "catalog.validate" else 1))
    return run, True


def get(owner_id: UUID, run_id: UUID) -> dict | None:
    with connection("gtm_api", owner_id) as conn:
        # One statement snapshot for parent, child statuses and visible evidence references.
        return conn.execute(f"""select {RUN_FIELDS},
            (select coalesce(jsonb_agg(jsonb_build_object(
                'id',j.id,'operation',j.task_type,'status',j.state,'attempt',j.attempt,
                'max_attempts',j.max_attempts,'error_code',j.error_code,
                'updated_at',j.updated_at,'heartbeat_at',j.heartbeat_at,
                'lease_expires_at',j.lease_expires_at,
                'lease_expired',j.state='running' and j.lease_expires_at<=clock_timestamp())
                order by j.created_at,j.id),'[]'::jsonb)
                from gtm.jobs j where j.run_id=r.id) as jobs,
            (select coalesce(jsonb_agg(a.id order by a.created_at,a.id),'[]'::jsonb)
                from gtm.artifacts a where a.run_id=r.id) as artifact_ids
            from gtm.runs r where id=%s""", (run_id,)).fetchone()


def list_runs(owner_id: UUID, project_id: UUID, limit: int = 20) -> list[dict]:
    if not 1 <= limit <= 100:
        raise RunError("invalid_run_limit")
    with connection("gtm_api", owner_id) as conn:
        if conn.execute("select id from gtm.projects where id=%s", (project_id,)).fetchone() is None:
            raise RunError("not_found")
        return conn.execute(f"""select {RUN_FIELDS} from gtm.runs where project_id=%s
            order by created_at desc,id desc limit %s""", (project_id, limit)).fetchall()
