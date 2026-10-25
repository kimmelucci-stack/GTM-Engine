"""Job-title based buying-committee contracts; no automatic authority assignment."""

import json
from importlib.resources import files
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from gtm_engine.domain.business_functions import Department, GovernanceBody


class JobTitle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_title_id: str
    title_en: str = Field(min_length=1)
    title_it: str = Field(min_length=1)
    aliases: list[str]
    department_ids: list[str] = Field(min_length=1)
    level: Literal["ownership", "board", "executive", "director", "head", "manager",
                   "team_lead", "supervisor", "coordinator", "specialist"]


class JobTitleDirectory(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal["buyer-job-titles-v1"]
    kind: Literal["internal_reference"]
    departments: list[Department]
    job_titles: list[JobTitle]
    governance_bodies: list[GovernanceBody]
    limitations: list[str]

    @model_validator(mode="after")
    def references(self):
        departments = {d.department_id for d in self.departments}
        if len(departments) != len(self.departments):
            raise ValueError("Duplicate department")
        if len({t.job_title_id for t in self.job_titles}) != len(self.job_titles):
            raise ValueError("Duplicate job title")
        for title in self.job_titles:
            if (not set(title.department_ids) <= departments
                    or len(set(title.department_ids)) != len(title.department_ids)):
                raise ValueError("Invalid title department")
        return self


def load_job_titles() -> JobTitleDirectory:
    raw = files("gtm_engine.domain").joinpath("buyer_job_titles.v1.json").read_text(encoding="utf-8")
    return JobTitleDirectory.model_validate(json.loads(raw))


class CommitteeMember(BaseModel):
    model_config = ConfigDict(extra="forbid")
    member_id: str = Field(min_length=1)
    department_id: str
    job_title_id: str | None = None
    custom_job_title: str | None = None
    buying_roles: list[Literal["initiator", "champion", "influencer", "evaluator", "decision_maker",
                               "budget_approver", "purchaser", "user", "gatekeeper"]] = Field(
                                   default_factory=list)
    rationale: str = Field(min_length=1)
    needs: list[str] = Field(default_factory=list)
    criteria: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    status: Literal["Observed", "Inferred", "Unverified"] = "Unverified"

    @model_validator(mode="after")
    def concrete_title(self):
        directory = load_job_titles()
        if self.department_id not in {d.department_id for d in directory.departments}:
            raise ValueError("Unknown department")
        if bool(self.job_title_id) == bool(self.custom_job_title and self.custom_job_title.strip()):
            raise ValueError("Exactly one concrete job title is required")
        if self.job_title_id:
            title = next((t for t in directory.job_titles if t.job_title_id == self.job_title_id), None)
            if title is None or self.department_id not in title.department_ids:
                raise ValueError("Unknown job title or inconsistent department")
        if len(set(self.buying_roles)) != len(self.buying_roles):
            raise ValueError("Duplicate buying role")
        if self.status == "Observed" and not any(ref.strip() for ref in self.source_refs):
            raise ValueError("Observed committee membership requires evidence")
        return self


class ApproachStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order: int = Field(ge=1)
    member_ids: list[str] = Field(min_length=1)
    objective: str = Field(min_length=1)
    evidence_to_present: list[str] = Field(default_factory=list)
    rationale: str = Field(min_length=1)


class BuyingCommittee(BaseModel):
    """Offer-specific proposal; not a lead list, organization chart or messaging sender."""

    model_config = ConfigDict(extra="forbid")
    directory_version: Literal["buyer-job-titles-v1"] = "buyer-job-titles-v1"
    offer_context: str = Field(min_length=1)
    purchase_occasion: str = Field(min_length=1)
    members: list[CommitteeMember] = Field(min_length=1)
    approach: list[ApproachStep] = Field(default_factory=list)
    limitations: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def consistent_approach(self):
        ids = {m.member_id for m in self.members}
        if len(ids) != len(self.members):
            raise ValueError("Duplicate committee member")
        if len({s.order for s in self.approach}) != len(self.approach):
            raise ValueError("Duplicate approach step order")
        for step in self.approach:
            if not set(step.member_ids) <= ids or len(set(step.member_ids)) != len(step.member_ids):
                raise ValueError("Unknown or duplicate approach recipient")
        return self
