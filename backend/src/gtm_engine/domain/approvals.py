"""Pure approval guards. Trusted server code must persist records before jobs.

Not an authentication mechanism or a public API accepting client-made approvals.
Persistence/authenticated owner and worker integration are Gate 2/4 work.
"""

import hashlib
import json
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from gtm_engine.domain.competitors import Candidate, SelectionReview, domain_key


def proposal_revision(review: SelectionReview, manual: tuple[Candidate, ...] = ()) -> str:
    payload = {"proposal": review.model_dump(mode="json"),
               "manual": [c.model_dump(mode="json") for c in manual]}
    # Sets from models serialize to unordered arrays; canonicalize every array
    # for this evidence-set revision (order is not a rank or owner preference).
    def canonical(value):
        if isinstance(value, dict):
            return {k: canonical(v) for k, v in value.items()}
        if isinstance(value, list):
            return sorted((canonical(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))
        return value
    encoded = json.dumps(canonical(payload), sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


class ApprovedSelection(BaseModel):
    model_config = ConfigDict(frozen=True)
    analysis_id: str
    proposal_revision: str
    selected_ids: tuple[str, ...] = Field(min_length=1, max_length=8)
    approved_at: datetime


def approve_selection(review: SelectionReview, selected_ids: tuple[str, ...], *,
                      expected_revision: str, manual: tuple[Candidate, ...] = ()) -> ApprovedSelection:
    revision = proposal_revision(review, manual)
    if expected_revision != revision or review.review_state == "rejected":
        raise ValueError("Proposal changed or rejected; explicit review required")
    if len(manual) > 3:
        raise ValueError("At most three manually added profiles")
    pool = [*review.candidates, *manual]
    ids = [c.candidate_id for c in pool]
    domains = [domain_key(c.domain) for c in pool]
    if len(set(ids)) != len(ids) or len(set(domains)) != len(domains):
        raise ValueError("Duplicate identity")
    client = {domain_key(d) for d in review.client_domains}
    if any(c.analysis_id != review.analysis_id or domain_key(c.domain) in client for c in pool):
        raise ValueError("Wrong offer or client identity")
    chosen = set(selected_ids)
    if len(chosen) != len(selected_ids) or not chosen or not chosen <= set(ids):
        raise ValueError("Empty, duplicate or unknown selection")
    if any(not c.eligible for c in pool if c.candidate_id in chosen):
        raise ValueError("Selected profile awaits qualification")
    base_ids = {c.candidate_id for c in review.candidates}
    required = min(5, sum(c.eligible for c in review.candidates))
    if len(chosen & base_ids) != required:
        raise ValueError("Select five base profiles, or the verified partial sample")
    return ApprovedSelection(analysis_id=review.analysis_id, proposal_revision=revision,
                             selected_ids=selected_ids, approved_at=datetime.now(UTC))


def require_current_approval(review: SelectionReview, approval: ApprovedSelection | None, *,
                             requested_ids: tuple[str, ...],
                             manual: tuple[Candidate, ...] = ()) -> None:
    if approval is None:
        raise ValueError("Owner approval required before detailed collection")
    if (approval.analysis_id != review.analysis_id
            or approval.proposal_revision != proposal_revision(review, manual)):
        raise ValueError("Approval obsolete; explicit review required")
    if (not requested_ids or len(set(requested_ids)) != len(requested_ids)
            or not set(requested_ids) <= set(approval.selected_ids)):
        raise ValueError("Collection contains unapproved profiles")
    # Recheck eligibility, caps and identities at use time, even for stored records.
    approve_selection(review, approval.selected_ids, expected_revision=approval.proposal_revision,
                      manual=manual)
