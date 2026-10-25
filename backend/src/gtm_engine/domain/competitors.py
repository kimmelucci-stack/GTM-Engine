"""competitor-selection-v1: screening/review contracts, not a ranking algorithm.

An agent proposes classifications with source references. These validators check
consistency, not the truth of the classification or commercial effectiveness.
No provider access, scoring v1.1 change, persistence or production workflow here.
"""

from enum import StrEnum
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, model_validator

METHOD_VERSION = "competitor-selection-v1"


class Relation(StrEnum):
    DIRECT = "direct"
    SUBSTITUTE = "substitute"


class ChannelSample(BaseModel):
    # Exploratory web search must never be reported as a measured Google channel.
    channel: Literal["organic", "maps", "paid", "exploratory_web"]
    status: Literal["not_checked", "unavailable", "sampled"] = "not_checked"
    checked_queries: set[str] = Field(default_factory=set)
    present_queries: set[str] = Field(default_factory=set)
    source_refs: list[str] = Field(default_factory=list)
    collection_context: str | None = None

    @model_validator(mode="after")
    def consistent_sample(self):
        if self.status == "sampled":
            if not self.checked_queries or not self.source_refs or not self.collection_context:
                raise ValueError("Sample requires checked queries, source refs and context")
        elif self.checked_queries or self.present_queries:
            raise ValueError("Unknown/unavailable channel cannot contain sampled counts")
        if not self.present_queries <= self.checked_queries:
            raise ValueError("Presence must belong to the checked query sample")
        return self

    @property
    def presence(self) -> str:
        if self.status != "sampled":
            return "unknown"
        return "observed_in_sample" if self.present_queries else "not_observed_in_sample"


class Candidate(BaseModel):
    candidate_id: str = Field(min_length=1)
    analysis_id: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    role: Literal["seller", "intermediary", "publisher", "unresolved"]
    relation: Relation | None = None
    substitutability: Literal["verified", "uncertain", "not_relevant"] = "uncertain"
    identity_resolved: bool = False
    represents_client: bool = False
    audience_occasion_verified: bool = False
    territory_verified: bool = False
    rationale: str = Field(min_length=1)
    source_refs: list[str] = Field(default_factory=list)
    channels: list[ChannelSample] = Field(default_factory=list)

    @model_validator(mode="after")
    def classification(self):
        if self.represents_client and self.substitutability == "verified":
            raise ValueError("Client listings cannot be qualified competitors")
        if len({s.channel for s in self.channels}) != len(self.channels):
            raise ValueError("Duplicate channel sample")
        if self.substitutability == "verified" and (
                    not self.source_refs or self.relation is None or not self.identity_resolved
                    or not self.audience_occasion_verified or not self.territory_verified
                    or self.role not in ("seller", "intermediary")):
            raise ValueError("Verified alternative requires sourced commercial qualification")
        return self

    @property
    def eligible(self) -> bool:
        # Visibility deliberately does not determine commercial eligibility.
        return self.substitutability == "verified"


def domain_key(value: str) -> str:
    """Normalize known website identity only; never infer shared legal ownership."""
    parsed = urlsplit(value if "://" in value else "https://" + value)
    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Invalid website identity")
    return parsed.hostname.lower().removeprefix("www.")


class SelectionReview(BaseModel):
    method_version: Literal["competitor-selection-v1"] = METHOD_VERSION
    analysis_id: str = Field(min_length=1)
    offer_context: str = Field(min_length=1)
    query_sample_version: str = Field(min_length=1)
    client_domains: set[str] = Field(min_length=1)
    candidates: list[Candidate]
    selected_ids: list[str] = Field(max_length=5)
    # Every screened candidate gets an inclusion/exclusion reason; AI prose is
    # not proof, so review of these reasons remains a human acceptance step.
    decisions: dict[str, str]
    omitted_class_reasons: dict[Relation, str] = Field(default_factory=dict)
    limitations: list[str] = Field(min_length=1)
    review_state: Literal["proposed", "approved", "rejected"] = "proposed"

    @model_validator(mode="after")
    def review_contract(self):
        ids = {c.candidate_id for c in self.candidates}
        if len(ids) != len(self.candidates) or len(set(self.selected_ids)) != len(self.selected_ids):
            raise ValueError("Duplicate candidate or selection ID")
        if not set(self.selected_ids) <= ids:
            raise ValueError("Unknown selected candidate")
        if set(self.decisions) != ids or any(not r.strip() for r in self.decisions.values()):
            raise ValueError("Every candidate needs an inclusion/exclusion reason")
        client = {domain_key(d) for d in self.client_domains}
        domains = set()
        for candidate in self.candidates:
            if candidate.analysis_id != self.analysis_id:
                raise ValueError("Mixed offer analyses")
            domain = domain_key(candidate.domain)
            if domain in client or domain in domains:
                raise ValueError("Client or duplicate website in candidate pool")
            domains.add(domain)
        selected = [c for c in self.candidates if c.candidate_id in self.selected_ids]
        if any(not c.eligible for c in selected):
            raise ValueError("Selected profiles must be qualified commercial alternatives")
        eligible = [c for c in self.candidates if c.eligible]
        if len(selected) < min(5, len(eligible)):
            raise ValueError("Qualified candidates cannot be omitted from a short partial list")
        omitted = {c.relation for c in eligible} - {c.relation for c in selected}
        if any(not self.omitted_class_reasons.get(r, "").strip() for r in omitted):
            raise ValueError("Explain omission of a relevant commercial class")
        return self

    @property
    def coverage_status(self) -> str:
        return "five_proposed" if len(self.selected_ids) == 5 else "partial"
