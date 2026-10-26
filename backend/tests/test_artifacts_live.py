"""Opt-in hosted DB/Storage tests. Only freshly seeded synthetic trees are allowed."""

import importlib
import json
import os
from pathlib import Path
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi.testclient import TestClient

from gtm_engine.api import app
from gtm_engine.auth import verified_owner
from gtm_engine.persistence.artifacts import ArtifactError, Evidence, PostgresArtifacts, archive
from gtm_engine.persistence.database import connection
from gtm_engine.persistence.queue import PostgresQueue
from gtm_engine.persistence.storage import BUCKET, PrivateStorage
from gtm_engine.worker import handlers, run_once

pytestmark = pytest.mark.skipif(os.environ.get("GTM_STORAGE_TEST") != "1",
                                reason="Opt-in real DB/Storage test")


@pytest.fixture(scope="module")
def live():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    os.environ.update({k: v for k, v in importlib.import_module("run_backend").local_settings().items()
                       if not os.environ.get(k)})
    fixture = json.loads(Path(os.environ["GTM_STORAGE_FIXTURE"]).read_text())
    UUID(fixture["owner_id"])
    UUID(fixture["project_id"])
    assert len(fixture["jobs"]) == 2
    yield fixture
    app.dependency_overrides.clear()
    # Delete only objects belonging to this exact synthetic run tree, via Storage API.
    run_ids = [UUID(j["run_id"]) for j in fixture["jobs"]]
    with connection("gtm_worker") as conn:
        rows = conn.execute("select storage_key from gtm.artifacts where run_id=any(%s)",
                            (run_ids,)).fetchall()
    if rows:
        status, _ = PrivateStorage.configured()._request("DELETE", "object/" + BUCKET,
            maximum=16384, json={"prefixes": [r["storage_key"] for r in rows]})
        assert status == 200


def test_worker_to_storage_owner_api_and_public_denial(live):
    queue = PostgresQueue()
    assert run_once(queue, handlers()) == "completed"
    run_id = UUID(next(j["run_id"] for j in live["jobs"] if j["task_type"] == "catalog.archive"))
    with connection("gtm_worker") as conn:
        row = conn.execute("select * from gtm.artifacts where run_id=%s", (run_id,)).fetchone()
    assert row and row["state"] == "ready"
    assert row["verified_at"] is not None
    repo = PostgresArtifacts()
    assert repo.get(uuid4(), row["id"]) is None
    assert repo.get(UUID(live["owner_id"]), row["id"])["sha256"] == row["sha256"]
    app.dependency_overrides[verified_owner] = lambda: UUID(live["owner_id"])
    try:
        with TestClient(app) as client:
            path = "/artifacts/" + str(row["id"])
            assert client.get(path).status_code == 200
            result = client.get(path + "/content")
            assert result.status_code == 200
            assert result.json()["job_title_count"] > 0
            assert "no-store" in result.headers["cache-control"]
            app.dependency_overrides[verified_owner] = uuid4
            assert client.get(path + "/content").status_code == 404
    finally:
        app.dependency_overrides.clear()
    with httpx.Client(timeout=15, trust_env=False, follow_redirects=False) as client:
        base = os.environ["SUPABASE_URL"].rstrip("/") + "/storage/v1/"
        headers = {"apikey": os.environ["SUPABASE_PUBLISHABLE_KEY"]}
        for prefix in ("object/public/", "object/authenticated/"):
            assert client.get(base + prefix + BUCKET + "/" + row["storage_key"],
                              headers=headers).status_code != 200


def test_pending_recovery_immutable_object_and_stale_lease(live):
    queue, repo, storage = PostgresQueue(), PostgresArtifacts(), PrivateStorage.configured()
    job = queue.claim(["artifact.synthetic"])
    assert job is not None
    evidence = Evidence(provider="synthetic", endpoint="synthetic.archive", query={},
        fetched_at="2026-10-26T00:00:00Z", requested_geo={}, effective_geo=None, period=None,
        availability="available", nature="observed", limitations=["Synthetic test, no market data"])
    identifier, body = uuid4(), b'{"synthetic":true}'
    row = repo.prepare(job, identifier, kind="raw", body=body,
                       content_type="application/json", evidence=evidence)
    assert repo.get(UUID(live["owner_id"]), identifier) is None
    # Simulate commit after upload, before readiness. Existing object must be read and verified.
    storage.upload_verified(row["storage_key"], body, "application/json")
    result = archive(job, identifier, kind="raw", body=body, content_type="application/json",
                     evidence=evidence, repository=repo, storage=storage)
    assert result["state"] == "ready"
    with pytest.raises(ArtifactError, match="conflicting_artifact"):
        repo.prepare(job, identifier, kind="raw", body=b"different",
                     content_type="application/json", evidence=evidence)
    assert queue.finish(job, "completed")
    with pytest.raises(ArtifactError, match="lease_lost"):
        repo.ready(job, identifier)
    with connection("gtm_worker") as conn:
        assert conn.execute("select state from gtm.artifacts where id=%s",
                            (identifier,)).fetchone()["state"] == "ready"
