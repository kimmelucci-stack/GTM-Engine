"""Each operation commits independently. Lease tokens fence stale workers."""

from dataclasses import dataclass
from uuid import UUID

from gtm_engine.persistence.database import connection


@dataclass(frozen=True)
class Job:
    id: UUID
    run_id: UUID
    task_type: str
    lease_token: UUID
    attempt: int
    max_attempts: int


class PostgresQueue:
    def claim(self, task_types: list[str]) -> Job | None:
        with connection("gtm_worker") as conn:
            row = conn.execute("select * from gtm.claim_job(%s)", (task_types,)).fetchone()
        if row is None:
            return None
        return Job(**{k: row[k] for k in Job.__dataclass_fields__})

    def heartbeat(self, job: Job) -> bool:
        with connection("gtm_worker") as conn:
            return conn.execute("select gtm.heartbeat_job(%s,%s) as ok",
                                (job.id, job.lease_token)).fetchone()["ok"]

    def finish(self, job: Job, state: str, error: str | None = None) -> bool:
        with connection("gtm_worker") as conn:
            return conn.execute("select gtm.finish_job(%s,%s,%s,%s) as ok",
                                (job.id, job.lease_token, state, error)).fetchone()["ok"]

    def expire(self) -> int:
        with connection("gtm_worker") as conn:
            return conn.execute("select gtm.expire_jobs() as count").fetchone()["count"]
