"""Process health and public reference data; no external-service readiness claim."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from gtm_engine.domain.business_functions import (
    VERSION,
    DirectoryVersion,
    FunctionDirectory,
    load_directory,
)
from gtm_engine.domain.buying_committee import JobTitleDirectory, load_job_titles

app = FastAPI(title="GTM Engine", version="0.1.0")


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
