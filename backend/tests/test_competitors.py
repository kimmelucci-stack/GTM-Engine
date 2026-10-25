import pytest
from pydantic import ValidationError

from gtm_engine.domain.competitors import Candidate, ChannelSample, SelectionReview


def candidate(index=1, **overrides):
    fields = {"candidate_id": str(index), "analysis_id": "offer-a", "domain": f"site{index}.test",
                  "role": "seller", "relation": "direct", "substitutability": "verified",
                  "identity_resolved": True, "audience_occasion_verified": True, "territory_verified": True,
                  "rationale": "Synthetic offer matches purchase occasion and area.",
                  "source_refs": ["synthetic:offer"]}
    return Candidate(**(fields | overrides))


def review(candidates, selected=None, **overrides):
    fields = {"analysis_id": "offer-a", "offer_context": "Synthetic offer, audience and territory",
                  "query_sample_version": "sample-v1", "client_domains": {"client.test"},
                  "candidates": candidates,
                  "selected_ids": [c.candidate_id for c in candidates] if selected is None else selected,
                  "decisions": {c.candidate_id: "Synthetic reason for inclusion or exclusion."
                             for c in candidates}, "limitations": ["Synthetic contract test only."]}
    return SelectionReview(**(fields | overrides))


def test_direct_candidate_without_visibility_remains_eligible():
    assert candidate().eligible
    assert ChannelSample(channel="organic").presence == "unknown"


def test_substitute_is_eligible_without_same_industry():
    assert review([candidate(relation="substitute")]).coverage_status == "partial"


def test_high_visibility_publisher_is_not_commercial_competitor():
    sample = ChannelSample(channel="organic", status="sampled", checked_queries={"q"},
                           present_queries={"q"}, source_refs=["synthetic:serp"],
                           collection_context="UTC, provider, geo, language, device, depth")
    publisher = candidate(role="publisher", relation=None, substitutability="not_relevant",
                          channels=[sample])
    with pytest.raises(ValidationError, match="qualified commercial"):
        review([publisher])


def test_intermediary_requires_actual_commercial_qualification():
    assert candidate(role="intermediary").eligible
    with pytest.raises(ValidationError, match="commercial qualification"):
        candidate(role="intermediary", source_refs=[])


def test_absence_in_checked_sample_is_not_unknown_or_market_absence():
    sample = ChannelSample(channel="organic", status="sampled", checked_queries={"q"},
                           source_refs=["synthetic:serp"], collection_context="Synthetic context")
    assert sample.presence == "not_observed_in_sample"
    with pytest.raises(ValidationError):
        ChannelSample(channel="paid", status="not_checked", present_queries={"q"})


@pytest.mark.parametrize("overrides", [
    {"domain": "https://www.client.test/"}, {"analysis_id": "other-offer"}
])
def test_client_and_other_offer_are_rejected(overrides):
    with pytest.raises(ValidationError):
        review([candidate(**overrides)])


def test_unresolved_identity_cannot_be_verified_alternative():
    with pytest.raises(ValidationError):
        candidate(identity_resolved=False)


def test_five_similar_profiles_need_reason_to_omit_verified_substitute():
    candidates = [candidate(i) for i in range(5)] + [candidate(5, relation="substitute")]
    selected = [str(i) for i in range(5)]
    with pytest.raises(ValidationError, match="Explain omission"):
        review(candidates, selected)
    assert review(candidates, selected, omitted_class_reasons={
        "substitute": "Synthetic explicit coverage tradeoff for owner review."
    }).coverage_status == "five_proposed"


def test_proposal_does_not_imply_owner_approval():
    assert review([candidate()]).review_state == "proposed"
    with pytest.raises(ValidationError):
        review([candidate()], decisions={})
