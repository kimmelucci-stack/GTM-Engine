"""Opt-in real Postgres checks. Requires synthetic MCP seed metadata, never credentials in fixtures."""

import importlib.util
import json
import os
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
from threading import Barrier
from uuid import UUID, uuid4

import pytest

from gtm_engine.budgeted_calls import BudgetedCallError, CostRequest, execute_budgeted
from gtm_engine.domain.run_budget import RunBudgetError
from gtm_engine.persistence.budgets import PostgresBudget
from gtm_engine.persistence.database import PersistenceUnavailable, connection

pytestmark = pytest.mark.skipif(os.environ.get('GTM_DB_TEST') != '1', reason='Postgres opt-in')


@pytest.fixture(scope='module')
def seeded():
    path = os.environ.get('GTM_BUDGET_FIXTURE')
    if not path:
        pytest.skip('Synthetic seed metadata required')
    metadata = json.loads(Path(path).read_text(encoding='utf-8'))
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('budget_live_settings', root / 'scripts/run_backend.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    os.environ.update({k: v for k, v in module.local_settings().items() if not os.environ.get(k)})
    return metadata


def case(seeded, name):
    entry = next(c for c in seeded['cases'] if c['name'] == name)
    return UUID(entry['budget_id']), [UUID(r) for r in entry['runs']]


def reserve(repo, budget, run, event='synthetic', ceiling='10', component='data'):
    repo.reserve(budget, run, event, provider='synthetic', endpoint='/synthetic',
                 component=component, ceiling=Decimal(ceiling))


def test_parallel_reservations_share_one_cap(seeded):
    budget, runs = case(seeded, 'parallel')
    barrier = Barrier(2)
    def contender(index):
        barrier.wait(timeout=10)
        try:
            reserve(PostgresBudget(), budget, runs[index], str(index))
            return 'reserved'
        except RunBudgetError as exc:
            return str(exc)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(contender, range(2)))
    assert outcomes.count('reserved') == 1
    assert outcomes.count('run_budget_or_request_limit') == 1
    assert PostgresBudget().summary(budget)['committed_usd'] == '10'


def test_duplicate_event_grants_only_once_even_in_parallel(seeded):
    budget, runs = case(seeded, 'duplicate')
    barrier = Barrier(2)
    def contender(index):
        barrier.wait(timeout=10)
        try:
            reserve(PostgresBudget(), budget, runs[0], ceiling='1')
            return 'reserved'
        except RunBudgetError as exc:
            return str(exc)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(contender, range(2)))
    assert outcomes.count('reserved') == 1
    assert outcomes.count('event_already_reserved_reconcile_before_retry') == 1
    assert PostgresBudget().summary(budget)['committed_usd'] == '1'


def test_uncertain_reservation_survives_new_repository(seeded):
    budget, runs = case(seeded, 'uncertain')
    repo = PostgresBudget()
    reserve(repo, budget, runs[0])
    repo.uncertain(budget, 'synthetic')
    assert PostgresBudget().summary(budget)['committed_usd'] == '10'
    with pytest.raises(RunBudgetError, match='already_reserved'):
        reserve(PostgresBudget(), budget, runs[0])
    with pytest.raises(RunBudgetError, match='request_limit'):
        reserve(PostgresBudget(), budget, runs[1], 'next', '6')


def test_actual_overrun_persists_then_halts(seeded):
    budget, runs = case(seeded, 'overrun')
    repo = PostgresBudget()
    reserve(repo, budget, runs[0], ceiling='10')
    summary = repo.reconcile(budget, 'synthetic', Decimal(16))
    assert summary['halted']
    assert PostgresBudget().summary(budget)['observed_usd'] == '16'
    with pytest.raises(RunBudgetError, match='halted'):
        reserve(repo, budget, runs[1], 'next', '0')


def test_reconcile_is_idempotent_and_rejects_conflicting_actual(seeded):
    budget, runs = case(seeded, 'reconcile')
    repo = PostgresBudget()
    reserve(repo, budget, runs[0])
    repo.reconcile(budget, 'synthetic', Decimal('2.123456789'))
    assert repo.reconcile(budget, 'synthetic', Decimal('2.123456789'))['observed_usd'] == '2.123456789'
    with pytest.raises(RunBudgetError, match='conflicting_actual'):
        repo.reconcile(budget, 'synthetic', Decimal(3))
    assert repo.summary(budget)['observed_usd'] == '2.123456789'


def test_required_components_and_unmeasured_costs_remain_distinct(seeded):
    budget, runs = case(seeded, 'components')
    repo = PostgresBudget()
    assert not repo.summary(budget)['budget_compliance_proven']
    for component in ('data', 'ai', 'execution', 'allocated_fixed'):
        reserve(repo, budget, runs[0], component, '0', component)
        repo.reconcile(budget, component, Decimal(0))
    assert repo.summary(budget)['budget_compliance_proven']
    repo.mark_unmeasured(budget, 'execution')
    assert not PostgresBudget().summary(budget)['budget_compliance_proven']


def test_request_limit_persists_after_settlement(seeded):
    budget, runs = case(seeded, 'limits')
    repo = PostgresBudget()
    reserve(repo, budget, runs[0], ceiling='0')
    repo.reconcile(budget, 'synthetic', Decimal(0))
    with pytest.raises(RunBudgetError, match='request_limit'):
        reserve(repo, budget, runs[1], 'next', '0')


def test_seven_module_runs_share_one_budget(seeded):
    budget, runs = case(seeded, 'modules')
    repo = PostgresBudget()
    assert len(runs) == 7
    for i in range(5):
        reserve(repo, budget, runs[i], str(i), '3')
    with pytest.raises(RunBudgetError, match='request_limit'):
        reserve(repo, budget, runs[6], 'sixteenth-dollar', '1')
    assert repo.summary(budget)['committed_usd'] == '15'


def test_mismatched_module_budget_and_cap_mutation_are_rejected(seeded):
    budget, runs = case(seeded, 'fk')
    other_budget, _ = case(seeded, 'parallel')
    with pytest.raises(PersistenceUnavailable):
        reserve(PostgresBudget(), other_budget, runs[0], 'mismatched', '0')
    assert PostgresBudget().summary(budget)['committed_usd'] == '0'
    with pytest.raises(PersistenceUnavailable), connection('gtm_worker') as conn:
        conn.execute('update gtm.budgets set cap_usd=14 where id=%s', (budget,))


def test_budget_creation_checks_owner_and_global_cap(seeded):
    repo = PostgresBudget()
    owner, project = UUID(seeded['owner_id']), UUID(seeded['project_id'])
    created = repo.create(owner, project, Decimal(10))
    assert repo.summary(created)['cap_usd'] == '10'
    with pytest.raises(RunBudgetError, match='invalid_run_limits'):
        repo.create(owner, project, Decimal(16))
    with pytest.raises(PersistenceUnavailable):
        repo.create(uuid4(), project, Decimal(10))


def test_real_ledger_keeps_uncertain_call_and_prevents_second_invocation(seeded):
    budget, runs = case(seeded, 'wrapper')
    invocation = CostRequest(budget, runs[0], 'synthetic', 'synthetic', '/test', 'data', Decimal(10))
    calls = []
    def provider():
        calls.append(1)
        raise TimeoutError('synthetic')
    with pytest.raises(BudgetedCallError, match='provider_outcome_uncertain'):
        execute_budgeted(PostgresBudget(), invocation, provider, lambda value: Decimal(0))
    with pytest.raises(RunBudgetError, match='already_reserved'):
        execute_budgeted(PostgresBudget(), invocation, provider, lambda value: Decimal(0))
    assert calls == [1]
    assert PostgresBudget().summary(budget)['committed_usd'] == '10'
