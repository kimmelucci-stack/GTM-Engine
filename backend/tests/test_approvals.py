import pytest
from test_competitors import candidate, review

from gtm_engine.domain.approvals import (
    approve_selection,
    proposal_revision,
    require_current_approval,
)


def test_explicit_approval_required_and_bound_to_offer_revision():
    proposal = review([candidate()])
    with pytest.raises(ValueError, match="Owner approval"):
        require_current_approval(proposal, None, requested_ids=("1",))
    approval = approve_selection(proposal, ("1",), expected_revision=proposal_revision(proposal))
    require_current_approval(proposal, approval, requested_ids=("1",))
    changed = proposal.model_copy(update={"offer_context": "New offer"})
    with pytest.raises(ValueError, match="obsolete"):
        require_current_approval(changed, approval, requested_ids=("1",))
    with pytest.raises(ValueError, match="unapproved"):
        require_current_approval(proposal, approval, requested_ids=("other",))
    with pytest.raises(ValueError, match="unapproved"):
        require_current_approval(proposal, approval, requested_ids=("1", "1"))


def test_replacement_and_three_qualified_manual_additions():
    candidates = [candidate(i) for i in range(6)]
    proposal = review(candidates, selected=[str(i) for i in range(5)])
    manual = tuple(candidate(i) for i in range(6, 9))
    ids = ("0", "1", "2", "3", "5", "6", "7", "8")
    approval = approve_selection(proposal, ids, manual=manual,
                                 expected_revision=proposal_revision(proposal, manual))
    assert len(approval.selected_ids) == 8
    with pytest.raises(ValueError):
        approve_selection(proposal, ("0", "1"), expected_revision=proposal_revision(proposal))


def test_manual_pending_or_client_cannot_be_approved():
    proposal = review([candidate()])
    for addition in (candidate(2, substitutability="uncertain"),
                     candidate(2, domain="www.client.test")):
        manual = (addition,)
        with pytest.raises(ValueError):
            approve_selection(proposal, ("1", "2"), manual=manual,
                              expected_revision=proposal_revision(proposal, manual))


def test_candidate_change_invalidates_consent():
    proposal = review([candidate()])
    old = proposal_revision(proposal)
    changed = review([candidate(rationale="Updated evidence requires review.")])
    with pytest.raises(ValueError, match="changed"):
        approve_selection(changed, ("1",), expected_revision=old)
