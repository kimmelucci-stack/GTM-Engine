from uuid import uuid4

import pytest

from gtm_engine.persistence.queue import Job
from gtm_engine.worker import Handler, SafeRetry, run_once


class QueueStub:
    def __init__(self, *, attempt=1, maximum=3, finish=True):
        self.job = Job(uuid4(), uuid4(), "synthetic", uuid4(), attempt, maximum)
        self.result = None
        self.finish_ok = finish
        self.claims = []
        self.expired = False

    def expire(self):
        self.expired = True
        return 0

    def claim(self, task_types):
        self.claims = task_types
        return self.job

    def heartbeat(self, job):
        return True

    def finish(self, job, state, error=None):
        self.result = (state, error)
        return self.finish_ok


def test_success_only_claims_supported_work():
    queue = QueueStub()
    assert run_once(queue, {"synthetic": Handler(lambda job: None)}) == "completed"
    assert queue.expired and queue.claims == ["synthetic"]
    assert queue.result == ("completed", None)


def test_empty_and_idle_do_not_report_completion():
    queue = QueueStub()
    assert run_once(queue, {}) == "no_handlers"
    queue.job = None
    assert run_once(queue, {"synthetic": Handler(lambda job: None)}) == "idle"
    assert queue.result is None


@pytest.mark.parametrize("safe,attempt,maximum,expected", [
    (False, 1, 3, ("failed", "outcome_unknown")),
    (True, 1, 3, ("queued", "retry_safe")),
    (True, 3, 3, ("failed", "retry_safe")),
])
def test_retries_require_explicit_safety_and_remaining_attempts(safe, attempt, maximum, expected):
    def handler(job):
        raise SafeRetry()
    queue = QueueStub(attempt=attempt, maximum=maximum)
    run_once(queue, {"synthetic": Handler(handler, safe)})
    assert queue.result == expected


def test_exception_details_never_enter_queue():
    def handler(job):
        raise RuntimeError("synthetic sensitive provider payload")
    queue = QueueStub()
    assert run_once(queue, {"synthetic": Handler(handler)}) == "failed"
    assert queue.result == ("failed", "handler_failed")


def test_stale_completion_is_not_reported_as_success():
    assert run_once(QueueStub(finish=False),
                    {"synthetic": Handler(lambda job: None)}) == "lease_lost"


def test_lost_heartbeat_prevents_completion():
    from threading import Event
    signalled = Event()
    queue = QueueStub()
    def heartbeat(job):
        signalled.set()
        return False
    queue.heartbeat = heartbeat
    assert run_once(queue, {"synthetic": Handler(lambda job: signalled.wait(2))},
                    heartbeat_seconds=0.01) == "lease_lost"
    assert queue.result is None
