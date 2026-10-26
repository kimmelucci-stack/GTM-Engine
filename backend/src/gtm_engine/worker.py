"""Bounded PostgreSQL worker. No analysis/provider handlers are enabled yet."""

import argparse
import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Event, Thread
from typing import Protocol
from uuid import uuid5

from gtm_engine.domain.buying_committee import load_job_titles
from gtm_engine.persistence.artifacts import Evidence, PostgresArtifacts, archive
from gtm_engine.persistence.database import PersistenceUnavailable
from gtm_engine.persistence.queue import Job, PostgresQueue
from gtm_engine.persistence.storage import PrivateStorage, StorageError


class Queue(Protocol):
    def claim(self, task_types: list[str]) -> Job | None: ...
    def heartbeat(self, job: Job) -> bool: ...
    def finish(self, job: Job, state: str, error: str | None = None) -> bool: ...
    def expire(self) -> int: ...


class SafeRetry(Exception):
    """Only for known retry-safe work, never an uncertain billable request."""


@dataclass(frozen=True)
class Handler:
    execute: Callable[[Job], None]
    retry_safe: bool = False


def run_once(queue: Queue, handlers: dict[str, Handler], heartbeat_seconds: float = 15) -> str:
    if not 0 < heartbeat_seconds < 30:
        raise ValueError("invalid_heartbeat_interval")
    queue.expire()
    if not handlers:
        return "no_handlers"
    job = queue.claim(list(handlers))
    if job is None:
        return "idle"
    stop, lost = Event(), Event()
    deadline = time.monotonic() + 300

    def renew() -> None:
        while not stop.wait(heartbeat_seconds):
            try:
                if time.monotonic() >= deadline or not queue.heartbeat(job):
                    lost.set()
                    return
            except Exception:  # noqa: BLE001 -- fail closed without logging provider/DB details
                lost.set()
                return

    thread = Thread(target=renew, daemon=True)
    thread.start()
    state, error = "completed", None
    try:
        handlers[job.task_type].execute(job)
    except SafeRetry:
        state, error = (("queued", "retry_safe") if handlers[job.task_type].retry_safe
                        else ("failed", "outcome_unknown"))
        if state == "queued" and job.attempt >= job.max_attempts:
            state = "failed"
    except Exception:  # noqa: BLE001 -- sanitize arbitrary handler exceptions at worker boundary
        state, error = "failed", "handler_failed"
    finally:
        stop.set()
        thread.join(timeout=12)
    if lost.is_set() or thread.is_alive() or time.monotonic() >= deadline:
        return "lease_lost"
    return state if queue.finish(job, state, error) else "lease_lost"


def check_catalog(job: Job) -> None:
    """Real local integrity check, not a generated GTM analysis."""
    if not load_job_titles().job_titles:
        raise ValueError("empty_catalog")


def archive_catalog(job: Job) -> None:
    """Archive a real local catalog check; no provider calls or GTM analysis."""
    catalog = load_job_titles()
    body = json.dumps({"kind": "catalog_integrity", "version": catalog.version,
                       "job_title_count": len(catalog.job_titles)},
                      sort_keys=True).encode()
    evidence = Evidence(provider="internal", endpoint="catalog.validate", query={},
                        fetched_at=datetime.now(UTC), requested_geo={}, effective_geo=None,
                        period=None, availability="available", nature="derived",
                        limitations=["Verifica del catalogo locale; nessuna analisi GTM."],
                        method="catalog-count", version="1")
    archive(job, uuid5(job.id, "catalog_integrity"), kind="derived", body=body,
            content_type="application/json", evidence=evidence,
            repository=PostgresArtifacts(), storage=PrivateStorage.configured())


def handlers() -> dict[str, Handler]:
    result = {"catalog.validate": Handler(check_catalog, True)}
    try:
        PrivateStorage.configured()
    except StorageError:
        return result
    # HTTP upload outcomes are never retried automatically.
    result["catalog.archive"] = Handler(archive_catalog)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the entry point only")
    parser.add_argument("--once", action="store_true", help="Process at most one supported job")
    args = parser.parse_args()
    if args.check:
        print("Worker entry point OK; no database connection or jobs executed.")
        return
    if not args.once:
        parser.error("Use --check or --once; continuous deployment is not configured")
    try:
        result = run_once(PostgresQueue(), handlers())
    except PersistenceUnavailable:
        parser.exit(2, "Worker database unavailable or not configured. No details logged.\n")
    print("Worker: " + result)


if __name__ == "__main__":
    main()
