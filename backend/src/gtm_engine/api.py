"""Process health and public reference data; no external-service readiness claim."""

import json
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator

from gtm_engine.auth import verified_owner
from gtm_engine.domain.business_functions import (
    VERSION,
    DirectoryVersion,
    FunctionDirectory,
    load_directory,
)
from gtm_engine.domain.buying_committee import JobTitleDirectory, load_job_titles
from gtm_engine.persistence import projects
from gtm_engine.persistence.artifacts import PostgresArtifacts
from gtm_engine.persistence.database import PersistenceUnavailable
from gtm_engine.persistence.storage import PrivateStorage, StorageError

app = FastAPI(title="GTM Engine", version="0.1.0")


class ProjectInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    offer_brief: dict
    product_in_development: bool
    geo: dict
    locale: str = Field(default="it-IT", min_length=2, max_length=32)

    @model_validator(mode="after")
    def bounded_payload(self):
        fields = self.model_dump(mode="json", include=set(ProjectInput.model_fields))
        if len(json.dumps(fields, ensure_ascii=False).encode()) > 65536:
            raise ValueError("Brief troppo grande")
        return self


class ProjectResponse(ProjectInput):
    id: UUID
    created_at: datetime


@app.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(body: ProjectInput, owner: Annotated[UUID, Depends(verified_owner)]):
    try:
        return projects.create_project(owner, body.model_dump())
    except PersistenceUnavailable:
        raise HTTPException(503, "Archivio progetti non disponibile") from None


@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID, owner: Annotated[UUID, Depends(verified_owner)]):
    try:
        result = projects.get_project(owner, project_id)
    except PersistenceUnavailable:
        raise HTTPException(503, "Archivio progetti non disponibile") from None
    if result is None:
        raise HTTPException(404, "Progetto non disponibile")
    return result


def owned_artifact(owner: UUID, artifact_id: UUID) -> dict:
    try:
        row = PostgresArtifacts().get(owner, artifact_id)
    except PersistenceUnavailable:
        raise HTTPException(503, "Archivio evidenze non disponibile") from None
    if row is None:
        raise HTTPException(404, "Evidenza non disponibile")
    return row


@app.get("/artifacts/{artifact_id}")
def artifact_metadata(artifact_id: UUID, owner: Annotated[UUID, Depends(verified_owner)],
                      response: Response):
    row = owned_artifact(owner, artifact_id)
    response.headers["Cache-Control"] = "private, no-store"
    return {name: row[name] for name in ("id", "run_id", "kind", "sha256", "byte_size",
                                        "content_type", "evidence", "created_at", "verified_at")}


@app.get("/artifacts/{artifact_id}/content")
def artifact_content(artifact_id: UUID, owner: Annotated[UUID, Depends(verified_owner)]):
    row = owned_artifact(owner, artifact_id)
    try:
        body = PrivateStorage.configured().download(row["storage_key"],
                    expected_size=row["byte_size"], digest=row["sha256"])
    except StorageError:
        raise HTTPException(503, "Contenuto evidenza non disponibile") from None
    return Response(body, media_type=row["content_type"], headers={
        "Cache-Control": "private, no-store", "Content-Disposition": "attachment",
        "X-Content-Type-Options": "nosniff", "Content-Security-Policy": "sandbox"})


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="gtm-engine-api")


@app.get("/reference/buyer-job-titles", response_model=JobTitleDirectory)
def buyer_job_titles(department_id: str | None = None, q: str | None = None) -> JobTitleDirectory:
    directory = load_job_titles()
    if department_id is not None:
        if department_id not in {d.department_id for d in directory.departments}:
            raise HTTPException(status_code=404, detail="Reparto non presente nella directory")
        directory.job_titles = [t for t in directory.job_titles if department_id in t.department_ids]
    if q and q.strip():
        term = q.strip().casefold()
        directory.job_titles = [t for t in directory.job_titles if any(
            term in name.casefold() for name in [t.title_it, t.title_en, *t.aliases])]
    return directory


@app.get("/reference/business-functions", response_model=FunctionDirectory)
def business_functions(department_id: str | None = None,
                       version: DirectoryVersion = VERSION) -> FunctionDirectory:
    """Public internal taxonomy only; no account, project or buyer data exposed."""
    directory = load_directory(version)
    if department_id is not None:
        if department_id not in {d.department_id for d in directory.departments}:
            raise HTTPException(status_code=404, detail="Reparto non presente nella directory")
        # Keep all department labels to resolve cross-department associations.
        directory.functions = [f for f in directory.functions if department_id in f.department_ids]
        visible = {f.function_id for f in directory.functions}
        directory.governance_roles = [r for r in directory.governance_roles
                                     if visible.intersection(r.related_function_ids)]
        # Reference associations in a filtered view only point to visible functions.
        for role in directory.governance_roles:
            role.related_function_ids = [f for f in role.related_function_ids if f in visible]
    return directory
