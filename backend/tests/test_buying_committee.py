import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from gtm_engine.api import app
from gtm_engine.domain.buying_committee import BuyingCommittee, CommitteeMember, load_job_titles


def member(**fields):
    return CommitteeMember(**({"member_id": "training", "department_id": "people",
                               "job_title_id": "training_coordinator",
                               "rationale": "Synthetic training purchase occasion"} | fields))


def test_every_department_has_titles_and_operational_influencers_not_just_executives():
    directory = load_job_titles()
    assert len(directory.job_titles) == 251
    for department in directory.departments:
        assert any(department.department_id in t.department_ids for t in directory.job_titles)
        if department.department_id != "leadership":
            assert any(department.department_id in t.department_ids and t.level in
                       {"coordinator", "specialist", "supervisor", "team_lead"}
                       for t in directory.job_titles)


def test_title_does_not_automatically_grant_authority():
    reference = member()
    assert reference.buying_roles == [] and reference.status == "Unverified"


@pytest.mark.parametrize("fields", [
    {"job_title_id": None}, {"job_title_id": "learning_development"},
    {"department_id": "finance"}, {"status": "Observed"},
    {"custom_job_title": "Alternative", "job_title_id": "hr_manager"},
])
def test_functions_departments_and_unsourced_claims_cannot_replace_titles(fields):
    with pytest.raises(ValidationError):
        member(**fields)


def test_custom_title_extension_is_explicit():
    reference = member(job_title_id=None, custom_job_title="Synthetic Sector Purchasing Lead")
    assert reference.custom_job_title and reference.buying_roles == []


def test_approach_must_reference_real_proposed_members():
    fields = {"offer_context": "Synthetic corporate activity", "purchase_occasion": "Training",
              "members": [member()], "limitations": ["Hypothesis, not actual committee"]}
    committee = BuyingCommittee(**fields, approach=[{
        "order": 1, "member_ids": ["training"], "objective": "Understand evaluation criteria",
        "rationale": "Synthetic entry point"}])
    assert committee.approach[0].member_ids == ["training"]
    with pytest.raises(ValidationError, match="recipient"):
        BuyingCommittee(**fields, approach=[{
            "order": 1, "member_ids": ["missing"], "objective": "Synthetic objective",
            "rationale": "Synthetic reasoning"}])


def test_api_returns_searchable_job_titles_without_mutating_catalog():
    with TestClient(app) as client:
        response = client.get("/reference/buyer-job-titles?department_id=people&q=training")
        assert response.status_code == 200
        assert {t["job_title_id"] for t in response.json()["job_titles"]} >= {
            "training_coordinator", "training_manager", "training_specialist"}
        assert client.get("/reference/buyer-job-titles?department_id=missing").status_code == 404
        assert len(client.get("/reference/buyer-job-titles").json()["job_titles"]) == 251
