import hashlib
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from gtm_engine.api import app
from gtm_engine.auth import verified_owner
from gtm_engine.persistence.artifacts import Evidence, archive
from gtm_engine.persistence.storage import (
    BUCKET,
    CONTENT_TYPES,
    MAX_BYTES,
    PrivateStorage,
    StorageError,
)


def evidence(**values):
    return Evidence(provider="synthetic", endpoint="synthetic.check", query={},
                    fetched_at=datetime.now(UTC), requested_geo={}, effective_geo=None, period=None,
                    availability="partial", nature="observed", limitations=["Synthetic test"],
                    **values)


def storage(handler):
    return PrivateStorage("https://synthetic.invalid", "synthetic-server-credential",
                          transport=httpx.MockTransport(handler))


def bucket(**values):
    return {"id": BUCKET, "public": False, "file_size_limit": MAX_BYTES,
            "allowed_mime_types": sorted(CONTENT_TYPES), **values}


def object_key(body=b"synthetic"):
    return f"{uuid4()}/{uuid4()}/{hashlib.sha256(body).hexdigest()}"


@pytest.mark.parametrize("changes", [{"public": True}, {"file_size_limit": None},
                                     {"allowed_mime_types": None}, {"id": "other"}])
def test_unsafe_bucket_never_uploads(changes):
    calls = []
    def handler(request):
        calls.append(request.method)
        return httpx.Response(200, json=bucket(**changes))
    with pytest.raises(StorageError, match="unsafe_storage_bucket"):
        storage(handler).upload_verified(object_key(), b"synthetic", "text/plain")
    assert calls == ["GET"]


def test_create_missing_bucket_and_verify_round_trip():
    calls, created = [], False
    body, key = b"synthetic", object_key()
    def handler(request):
        nonlocal created
        calls.append((request.method, request.url.path))
        if request.url.path.endswith("/bucket/" + BUCKET):
            return (httpx.Response(200, json=bucket()) if created else
                    httpx.Response(400, json={"code": "NoSuchBucket"}))
        if request.url.path.endswith("/bucket"):
            created = True
            return httpx.Response(200, json={})
        if request.method == "POST":
            assert request.headers["x-upsert"] == "false"
            assert request.content == body
            return httpx.Response(200, json={})
        return httpx.Response(200, content=body)
    storage(handler).upload_verified(key, body, "text/plain")
    assert [c[0] for c in calls] == ["GET", "POST", "GET", "POST", "GET"]


def test_duplicate_downloads_without_overwriting_and_rejects_wrong_hash():
    body, calls = b"synthetic", []
    def handler(request):
        calls.append(request.method)
        if "/bucket/" in request.url.path:
            return httpx.Response(200, json=bucket())
        if request.method == "POST":
            return httpx.Response(400, json={"code": "ResourceAlreadyExists"})
        return httpx.Response(200, content=b"different")
    with pytest.raises(StorageError, match="artifact_integrity_failed"):
        storage(handler).upload_verified(object_key(body), body, "text/plain")
    assert calls == ["GET", "POST", "GET"]


def test_timeout_is_not_retried_or_leaked():
    calls = []
    def handler(request):
        calls.append(request.method)
        raise httpx.ReadTimeout("synthetic sensitive secret", request=request)
    with pytest.raises(StorageError, match="storage_request_uncertain") as error:
        storage(handler).ensure_private_bucket()
    assert calls == ["GET"]
    assert "sensitive" not in str(error.value)


@pytest.mark.parametrize("key", ["../private", "https://synthetic.invalid/", "x?apikey=x"])
def test_arbitrary_paths_are_rejected_before_network(key):
    with pytest.raises(StorageError, match="invalid_storage_key"):
        storage(lambda r: pytest.fail("Network called")).download(key, expected_size=1, digest="x")


def test_oversized_download_is_bounded():
    with pytest.raises(StorageError, match="storage_response_too_large"):
        storage(lambda r: httpx.Response(200, content=b"xx")).download(
            object_key(), expected_size=1, digest="x")


def test_derived_metadata_requires_method_and_version():
    values = evidence().model_dump()
    values["nature"] = "derived"
    with pytest.raises(ValidationError):
        Evidence.model_validate(values)
    values.update(method="synthetic-method", version="1")
    assert Evidence.model_validate(values).nature == "derived"
    values["fetched_at"] = "2026-10-26T12:00:00+02:00"
    assert Evidence.model_validate(values).fetched_at.hour == 10
    values["fetched_at"] = datetime(2026, 1, 1)
    with pytest.raises(ValidationError):
        Evidence.model_validate(values)


def test_failure_leaves_manifest_pending_and_never_marks_ready():
    calls = []
    class Repository:
        def prepare(self, *args, **kwargs):
            calls.append("committed_pending")
            return {"storage_key": object_key()}
        def ready(self, *args):
            pytest.fail("Marked ready without verified upload")
    class Store:
        def upload_verified(self, *args):
            assert calls == ["committed_pending"]
            raise StorageError("storage_request_uncertain")
    with pytest.raises(StorageError):
        archive(None, uuid4(), kind="raw", body=b"synthetic", content_type="text/plain",
                evidence=evidence(), repository=Repository(), storage=Store())


def test_artifact_api_authentication_owner_gate_and_safe_download(monkeypatch):
    identifier, owner = uuid4(), uuid4()
    path = "/artifacts/" + str(identifier)
    body = b"synthetic"
    row = {"id": identifier, "run_id": uuid4(), "kind": "raw", "sha256": hashlib.sha256(body).hexdigest(),
           "byte_size": len(body), "content_type": "text/plain", "evidence": {},
           "created_at": datetime.now(UTC), "verified_at": datetime.now(UTC),
           "storage_key": object_key(body), "bucket": BUCKET}
    class Repo:
        def get(self, principal, artifact):
            assert principal == owner
            return row if artifact == identifier else None
    monkeypatch.setattr("gtm_engine.api.PostgresArtifacts", Repo)
    class Store:
        def download(self, key, **kwargs):
            assert key == row["storage_key"]
            return body
    monkeypatch.setattr("gtm_engine.api.PrivateStorage.configured", lambda: Store())
    try:
        with TestClient(app) as client:
            assert client.get(path).status_code == 401
            assert client.get(path + "/content").status_code == 401
            app.dependency_overrides[verified_owner] = lambda: owner
            metadata = client.get(path)
            assert metadata.status_code == 200
            assert "storage_key" not in metadata.json() and "bucket" not in metadata.json()
            assert "no-store" in metadata.headers["cache-control"]
            response = client.get(path + "/content")
            assert response.content == body
            assert response.headers["content-disposition"] == "attachment"
            assert response.headers["x-content-type-options"] == "nosniff"
            assert client.get("/artifacts/" + str(uuid4()) + "/content").status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_worker_only_enables_archive_with_storage_configuration(monkeypatch):
    from gtm_engine.worker import handlers
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    assert set(handlers()) == {"catalog.validate"}
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.invalid")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "synthetic")
    assert not handlers()["catalog.archive"].retry_safe
