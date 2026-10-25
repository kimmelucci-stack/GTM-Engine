"""Internal business-function directory; not a profession or authority classifier."""

import json
from importlib.resources import files
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

VERSION = "business-functions-v1.1"
DirectoryVersion = Literal["business-functions-v1", "business-functions-v1.1"]


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


class GovernanceBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    body_id: str = Field(pattern=r"^[a-z][a-z0-9_]+$")
    label: str = Field(min_length=1)
    responsibility: str = Field(min_length=1)


class GovernanceRole(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role_id: str = Field(pattern=r"^[a-z][a-z0-9_]+$")
    label: str = Field(min_length=1)
    category: Literal["ownership", "founding", "governance", "executive", "coordination"]
    responsibility: str = Field(min_length=1)
    related_function_ids: list[str] = Field(default_factory=list)
    body_ids: list[str] = Field(default_factory=list)


class FunctionDirectory(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: DirectoryVersion = VERSION
    kind: Literal["internal_reference"] = "internal_reference"
    limitations: list[str] = Field(min_length=1)
    departments: list[Department] = Field(min_length=1)
    functions: list[BusinessFunction]
    governance_bodies: list[GovernanceBody] = Field(default_factory=list)
    governance_roles: list[GovernanceRole] = Field(default_factory=list)

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
        bodies = {b.body_id for b in self.governance_bodies}
        roles = {r.role_id for r in self.governance_roles}
        functions = {f.function_id for f in self.functions}
        if len(bodies) != len(self.governance_bodies) or len(roles) != len(self.governance_roles):
            raise ValueError("Duplicate governance identity")
        for role in self.governance_roles:
            if (not set(role.body_ids) <= bodies or not set(role.related_function_ids) <= functions
                    or len(set(role.body_ids)) != len(role.body_ids)
                    or len(set(role.related_function_ids)) != len(role.related_function_ids)):
                raise ValueError("Invalid governance references")
        return self


def load_directory(version: DirectoryVersion = VERSION) -> FunctionDirectory:
    names = {"business-functions-v1": "business_functions.v1.json",
             "business-functions-v1.1": "business_functions.v1_1.json"}
    if version not in names:
        raise ValueError("Unsupported directory version")
    data = files("gtm_engine.domain").joinpath(names[version]).read_text(encoding="utf-8")
    return FunctionDirectory.model_validate(json.loads(data))


class BuyerFunctionReference(BaseModel):
    """Reference contract only; no discovery, owner authentication or inference here."""

    model_config = ConfigDict(extra="forbid")
    directory_version: DirectoryVersion = VERSION
    department_id: str | None = None
    function_id: str | None = None
    governance_role_ids: list[str] = Field(default_factory=list)
    governance_body_ids: list[str] = Field(default_factory=list)
    job_title: str | None = None
    buying_roles: list[Literal["initiator", "evaluator", "decision_maker", "budget_approver",
                               "purchaser", "user"]] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    source_refs: list[str] = Field(default_factory=list)
    status: Literal["Observed", "Inferred", "Unverified"] = "Unverified"

    @model_validator(mode="after")
    def qualified_reference(self):
        catalog = load_directory(self.directory_version)
        if self.function_id is not None or self.department_id is not None:
            function = next((f for f in catalog.functions if f.function_id == self.function_id), None)
            if function is None or self.department_id not in function.department_ids:
                raise ValueError("Unknown function or inconsistent department")
        if not self.function_id and not self.governance_role_ids and not self.governance_body_ids:
            raise ValueError("Function or governance reference required")
        for selected, valid in (
            (self.governance_role_ids, {r.role_id for r in catalog.governance_roles}),
            (self.governance_body_ids, {b.body_id for b in catalog.governance_bodies}),
        ):
            if not set(selected) <= valid or len(set(selected)) != len(selected):
                raise ValueError("Unknown or duplicate governance reference")
        if len(set(self.buying_roles)) != len(self.buying_roles):
            raise ValueError("Duplicate buying role")
        if self.status == "Observed" and not any(ref.strip() for ref in self.source_refs):
            raise ValueError("Observed assignment requires source references")
        return self
