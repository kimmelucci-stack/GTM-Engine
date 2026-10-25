from decimal import Decimal

import pytest

from gtm_engine.domain.run_budget import RunBudget, RunBudgetError


def reserve(budget, identifier="data", component="data", ceiling="2"):
    budget.reserve(identifier, provider="synthetic", component=component, ceiling=Decimal(ceiling))


def test_cross_provider_reservations_share_cap():
    budget = RunBudget(Decimal(15))
    reserve(budget, ceiling="10")
    budget.reserve("ai", provider="other-synthetic", component="ai", ceiling=Decimal(5))
    with pytest.raises(RunBudgetError, match="limit"):
        reserve(budget, "third", ceiling="0.01")
    assert budget.committed == Decimal(15)


def test_actual_cost_releases_unused_ceiling_and_is_idempotent():
    budget = RunBudget(Decimal(15))
    reserve(budget)
    budget.reconcile("data", Decimal("0.10"))
    budget.reconcile("data", Decimal("0.10"))
    assert budget.committed == Decimal("0.10")
    with pytest.raises(RunBudgetError, match="conflicting"):
        budget.reconcile("data", Decimal("0.20"))


def test_uncertain_request_keeps_reservation_and_cannot_be_retried_as_same_event():
    budget = RunBudget(Decimal(5))
    reserve(budget, ceiling="5")
    budget.uncertain("data")
    assert budget.committed == Decimal(5) and budget.observed == 0
    with pytest.raises(RunBudgetError, match="already_reserved"):
        reserve(budget, ceiling="5")
    assert not budget.summary()["budget_compliance_proven"]


def test_underestimated_cost_is_retained_and_halts_further_reservations():
    budget = RunBudget(Decimal(5))
    reserve(budget)
    budget.reconcile("data", Decimal(6))
    assert budget.observed == Decimal(6) and budget.halted
    with pytest.raises(RunBudgetError, match="halted"):
        reserve(budget, "next", ceiling="0")


def test_one_provider_reconciled_does_not_prove_whole_gtm_cost():
    budget = RunBudget(Decimal(15))
    reserve(budget)
    budget.reconcile("data", Decimal(0))
    report = budget.summary()
    assert not report["budget_compliance_proven"]
    assert set(report["missing_required_components"]) == {"ai", "execution", "allocated_fixed"}


def test_complete_measured_components_include_explicit_zero_and_unmeasured_is_not_zero():
    budget = RunBudget(Decimal(15))
    for component in budget.required_components:
        reserve(budget, component, component, "1")
        budget.reconcile(component, Decimal(0))
    assert budget.summary()["budget_compliance_proven"]
    budget.mark_unmeasured("unallocated_storage")
    assert not budget.summary()["fully_reconciled"]


@pytest.mark.parametrize("bad", [Decimal("NaN"), Decimal("Infinity"), Decimal(-1), 1.0])
def test_invalid_costs_rejected(bad):
    budget = RunBudget(Decimal(15))
    with pytest.raises(RunBudgetError):
        budget.reserve("x", provider="synthetic", component="data", ceiling=bad)


def test_request_cap_and_max_run_budget():
    with pytest.raises(RunBudgetError):
        RunBudget(Decimal("15.01"))
    budget = RunBudget(Decimal(15), max_requests=1)
    reserve(budget, ceiling="0")
    with pytest.raises(RunBudgetError):
        reserve(budget, "second", ceiling="0")
