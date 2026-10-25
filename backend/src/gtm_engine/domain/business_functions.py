"""Internal business-function directory; not a profession or authority classifier."""

import json
from importlib.resources import files
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

VERSION = "business-functions-v1"


class Department(BaseModel):
    model_config = ConfigDict(extra="forbid")
    department_id: str = Field(pattern=r"^[a-z][a-z0-9_]+$")
    label: str = Field(min_length=1)


class BusinessFunction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    function_id: str = Field(pattern=r"^[a-z][a-z0-9_]+$")
    label: str = Field(min_length=1)
    responsibility: str = Field(min_length=1)
    department_ids: list[str] = Field(min_length=1)


class FunctionDirectory(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal["business-functions-v1"] = VERSION
    kind: Literal["internal_reference"] = "internal_reference"
    limitations: list[str] = Field(min_length=1)
    departments: list[Department] = Field(min_length=1)
    functions: list[BusinessFunction]

    @model_validator(mode="after")
    def references(self):
        departments = {d.department_id for d in self.departments}
        if len(departments) != len(self.departments):
            raise ValueError("Duplicate department ID")
        if len({f.function_id for f in self.functions}) != len(self.functions):
            raise ValueError("Duplicate function ID")
        for function in self.functions:
            if (not set(function.department_ids) <= departments
                    or len(set(function.department_ids)) != len(function.department_ids)):
                raise ValueError("Invalid department references")
        return self


def load_directory() -> FunctionDirectory:
    data = files("gtm_engine.domain").joinpath("business_functions.v1.json").read_text(
        encoding="utf-8")
    return FunctionDirectory.model_validate(json.loads(data))


class BuyerFunctionReference(BaseModel):
    """Reference contract only; no discovery, owner authentication or inference here."""

    model_config = ConfigDict(extra="forbid")
    directory_version: Literal["business-functions-v1"] = VERSION
    department_id: str
    function_id: str
    job_title: str | None = None
    buying_roles: list[Literal["initiator", "evaluator", "decision_maker", "budget_approver",
                               "purchaser", "user"]] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    source_refs: list[str] = Field(default_factory=list)
    status: Literal["Observed", "Inferred", "Unverified"] = "Unverified"

    @model_validator(mode="after")
    def qualified_reference(self):
        catalog = load_directory()
        function = next((f for f in catalog.functions if f.function_id == self.function_id), None)
        if function is None or self.department_id not in function.department_ids:
            raise ValueError("Unknown function or inconsistent department")
        if len(set(self.buying_roles)) != len(self.buying_roles):
            raise ValueError("Duplicate buying role")
        if self.status == "Observed" and not any(ref.strip() for ref in self.source_refs):
            raise ValueError("Observed assignment requires source references")
        return self
