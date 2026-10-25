"""Process health only; does not certify access to external services."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from gtm_engine.domain.business_functions import FunctionDirectory, load_directory

app = FastAPI(title="GTM Engine", version="0.1.0")


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="gtm-engine-api")


@app.get("/reference/business-functions", response_model=FunctionDirectory)
def business_functions(department_id: str | None = None) -> FunctionDirectory:
    """Public internal taxonomy only; no account, project or buyer data exposed."""
    directory = load_directory()
    if department_id is not None:
        if department_id not in {d.department_id for d in directory.departments}:
            raise HTTPException(status_code=404, detail="Reparto non presente nella directory")
        # Keep all department labels to resolve cross-department associations.
        directory.functions = [f for f in directory.functions if department_id in f.department_ids]
    return directory
