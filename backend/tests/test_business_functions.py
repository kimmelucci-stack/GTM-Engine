import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from gtm_engine.api import app
from gtm_engine.domain.business_functions import (
    BuyerFunctionReference,
    FunctionDirectory,
    load_directory,
)


def test_directory_identifies_functions_separately_from_departments():
    directory = load_directory()
    assert directory.version == "business-functions-v1"
    assert len(directory.departments) == 12 and len(directory.functions) == 60
    assert {f.function_id for f in directory.functions}.isdisjoint(
        d.department_id for d in directory.departments)


def test_cross_department_function_has_one_canonical_identity():
    functions = [f for f in load_directory().functions if f.function_id == "internal_communication"]
    assert len(functions) == 1
    assert set(functions[0].department_ids) == {"people", "marketing"}


def test_function_assignment_does_not_infer_job_title_or_buying_authority():
    reference = BuyerFunctionReference(department_id="people", function_id="learning_development",
                                       rationale="Synthetic training occasion")
    assert reference.job_title is None
    assert reference.buying_roles == []
    assert reference.status == "Unverified"


@pytest.mark.parametrize("fields", [
    {"department_id": "finance", "function_id": "learning_development"},
    {"department_id": "people", "function_id": "unknown_function"},
    {"department_id": "people", "function_id": "learning_development", "status": "Observed"},
])
def test_invalid_or_unsourced_assignments_are_rejected(fields):
    with pytest.raises(ValidationError):
        BuyerFunctionReference(**fields, rationale="Synthetic qualification")


def test_directory_rejects_duplicate_functions_and_orphan_departments():
    data = load_directory().model_dump()
    data["functions"].append(data["functions"][0])
    with pytest.raises(ValidationError, match="Duplicate function"):
        FunctionDirectory.model_validate(data)
    data = load_directory().model_dump()
    data["functions"][0]["department_ids"] = ["unknown_department"]
    with pytest.raises(ValidationError, match="Invalid department"):
        FunctionDirectory.model_validate(data)


def test_reference_api_filters_shared_functions_without_requiring_esco():
    with TestClient(app) as client:
        response = client.get("/reference/business-functions", params={"department_id": "people"})
        assert response.status_code == 200
        data = response.json()
        assert all("people" in f["department_ids"] for f in data["functions"])
        assert "internal_communication" in {f["function_id"] for f in data["functions"]}
        assert client.get("/reference/business-functions?department_id=missing").status_code == 404
        full = client.get("/reference/business-functions").json()
        assert len(full["functions"]) == 60  # Filter did not mutate subsequent requests.
