from decimal import Decimal
from uuid import uuid4

import pytest

from gtm_engine.budgeted_calls import BudgetedCallError, CostRequest, execute_budgeted
from gtm_engine.domain.run_budget import RunBudget, RunBudgetError
from gtm_engine.persistence.database import PersistenceUnavailable


class LedgerStub:
    def __init__(self, cap="15"):
        self.domain = RunBudget(Decimal(cap))
        self.calls = []

    def reserve(self, budget_id, run_id, event_id, *, provider, endpoint, component, ceiling):
        self.domain.reserve(event_id, provider=provider, component=component, ceiling=ceiling)
        self.calls.append('committed')

    def reconcile(self, budget_id, event_id, actual):
        self.domain.reconcile(event_id, actual)
        return self.domain.summary()

    def uncertain(self, budget_id, event_id):
        self.domain.uncertain(event_id)


def request(ceiling="10", event_id="synthetic"):
    return CostRequest(uuid4(), uuid4(), event_id, 'synthetic', '/test', 'data', Decimal(ceiling))


def test_provider_runs_only_after_committed_reservation():
    ledger = LedgerStub()
    def provider():
        assert ledger.calls == ['committed']
        return {'synthetic': True}
    result = execute_budgeted(ledger, request(), provider, lambda response: Decimal('2.5'))
    assert result.value == {'synthetic': True}
    assert result.budget['observed_usd'] == '2.5'


def test_budget_denied_never_calls_provider():
    with pytest.raises(RunBudgetError):
        execute_budgeted(LedgerStub('5'), request(), lambda: pytest.fail('Provider called'),
                         lambda response: Decimal(1))


def test_uncertain_call_remains_reserved_and_never_retries():
    ledger = LedgerStub()
    invocation = request()
    calls = []
    def provider():
        calls.append(1)
        raise TimeoutError('synthetic sensitive provider detail')
    with pytest.raises(BudgetedCallError, match='provider_outcome_uncertain') as error:
        execute_budgeted(ledger, invocation, provider, lambda response: Decimal(1))
    assert 'sensitive' not in str(error.value)
    assert ledger.domain.committed == Decimal(10)
    assert ledger.domain.events['synthetic']['status'] == 'uncertain'
    with pytest.raises(RunBudgetError, match='already_reserved'):
        execute_budgeted(ledger, invocation, provider, lambda response: Decimal(1))
    assert calls == [1]


def test_missing_actual_is_not_zero():
    ledger = LedgerStub()
    with pytest.raises(BudgetedCallError, match='actual_cost_unavailable'):
        execute_budgeted(ledger, request(), lambda: None, lambda response: None)
    assert ledger.domain.observed == Decimal(0)
    assert ledger.domain.committed == Decimal(10)
    assert not ledger.domain.summary()['budget_compliance_proven']


def test_actual_above_ceiling_is_retained_and_halts_new_reservations():
    ledger = LedgerStub()
    result = execute_budgeted(ledger, request(), lambda: None, lambda response: Decimal(12))
    assert result.budget['halted']
    assert result.budget['observed_usd'] == '12'
    with pytest.raises(RunBudgetError, match='halted'):
        execute_budgeted(ledger, request('1', 'next'), lambda: pytest.fail('Provider called'),
                         lambda response: Decimal(1))


def test_reconciliation_failure_preserves_actual_for_recovery():
    ledger = LedgerStub()
    def unavailable(*args):
        raise PersistenceUnavailable('synthetic')
    ledger.reconcile = unavailable
    with pytest.raises(BudgetedCallError, match='cost_reconciliation_pending') as error:
        execute_budgeted(ledger, request(), lambda: None, lambda response: Decimal('2.5'))
    assert error.value.actual == Decimal('2.5')
    assert ledger.domain.committed == Decimal(10)
