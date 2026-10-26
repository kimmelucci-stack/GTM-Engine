"""Private manifests, owner-filtered reads and lease-fenced worker writes."""

import hashlib
from datetime import UTC
from typing import Literal
from uuid import UUID

from psycopg.types.json import Jsonb
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from gtm_engine.persistence.database import connection
from gtm_engine.persistence.queue import Job
from gtm_engine.persistence.storage import CONTENT_TYPES, MAX_BYTES, PrivateStorage


class ArtifactError(Exception):
    pass


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: str = Field(min_length=1, max_length=80)
    endpoint: str = Field(min_length=1, max_length=512)
    query: dict
    fetched_at: AwareDatetime
    requested_geo: dict
    effective_geo: dict | None
    period: dict | None
    availability: Literal["available", "partial", "unavailable"]
    nature: Literal["observed", "derived", "inferred"]
    limitations: list[str] = Field(max_length=50)
    method: str | None = Field(default=None, max_length=200)
    version: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def derivation(self) -> "Evidence":
        self.fetched_at = self.fetched_at.astimezone(UTC)
        if self.nature != "observed" and (not self.method or not self.version):
            raise ValueError("derivation_requires_method_version")
        if len(self.model_dump_json().encode()) > 32768:
            raise ValueError("evidence_metadata_too_large")
        return self


def _lease(conn, job: Job) -> None:
    row = conn.execute("""select id from gtm.jobs where id=%s and run_id=%s
        and state='running' and lease_token=%s and lease_expires_at>clock_timestamp()
        for update""", (job.id, job.run_id, job.lease_token)).fetchone()
    if row is None:
        raise ArtifactError("lease_lost")


class PostgresArtifacts:
    def prepare(self, job: Job, artifact_id: UUID, *, kind: str, body: bytes,
                content_type: str, evidence: Evidence) -> dict:
        if kind not in {"raw", "normalized", "derived", "deliverable"}:
            raise ArtifactError("invalid_artifact_kind")
        if not 0 < len(body) <= MAX_BYTES or content_type not in CONTENT_TYPES:
            raise ArtifactError("invalid_artifact_content")
        digest = hashlib.sha256(body).hexdigest()
        key = f"{job.run_id}/{artifact_id}/{digest}"
        values = evidence.model_dump(mode="json")
        with connection("gtm_worker") as conn:
            _lease(conn, job)
            conn.execute("""insert into gtm.artifacts
                (id,run_id,kind,storage_key,sha256,byte_size,content_type,evidence)
                values(%s,%s,%s,%s,%s,%s,%s,%s) on conflict(id) do nothing""",
                         (artifact_id, job.run_id, kind, key, digest, len(body),
                          content_type, Jsonb(values)))
            row = conn.execute("select * from gtm.artifacts where id=%s", (artifact_id,)).fetchone()
            if (row["run_id"] != job.run_id or row["kind"] != kind or row["sha256"] != digest
                    or row["content_type"] != content_type or row["byte_size"] != len(body)
                    or row["evidence"] != values):
                raise ArtifactError("conflicting_artifact")
        return row

    def ready(self, job: Job, artifact_id: UUID) -> None:
        with connection("gtm_worker") as conn:
            _lease(conn, job)
            row = conn.execute("""update gtm.artifacts set state='ready',
                verified_at=coalesce(verified_at,clock_timestamp()) where id=%s and run_id=%s
                returning id""", (artifact_id, job.run_id)).fetchone()
            if row is None:
                raise ArtifactError("unknown_artifact")

    def get(self, owner_id: UUID, artifact_id: UUID) -> dict | None:
        with connection("gtm_api", owner_id) as conn:
            return conn.execute("select * from gtm.artifacts where id=%s", (artifact_id,)).fetchone()


def archive(job: Job, artifact_id: UUID, *, kind: str, body: bytes, content_type: str,
            evidence: Evidence, repository: PostgresArtifacts, storage: PrivateStorage) -> dict:
    row = repository.prepare(job, artifact_id, kind=kind, body=body,
                             content_type=content_type, evidence=evidence)
    # Database transaction ended. Failure leaves the immutable manifest pending.
    storage.upload_verified(row["storage_key"], body, content_type)
    repository.ready(job, artifact_id)
    return {"id": artifact_id, "sha256": row["sha256"], "byte_size": len(body),
            "state": "ready"}
