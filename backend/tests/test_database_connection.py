from uuid import uuid4

import psycopg
import pytest

from gtm_engine.persistence.database import PersistenceUnavailable, connection


class ConnectionStub:
    def __init__(self, privileged=False):
        self.privileged = privileged
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query, params=None):
        self.calls.append((query, params))
        return self

    def fetchone(self):
        return {'rolsuper': False, 'rolbypassrls': self.privileged}


def test_connection_sets_tls_role_and_transaction_local_owner(monkeypatch):
    stub, observed = ConnectionStub(), {}
    def connect(dsn, **kwargs):
        observed.update(kwargs)
        return stub
    monkeypatch.setenv('DATABASE_URL', 'synthetic-not-a-real-connection')
    monkeypatch.setattr(psycopg, 'connect', connect)
    owner = uuid4()
    with connection('gtm_api', owner) as conn:
        assert conn is stub
    assert observed['sslmode'] == 'verify-full'
    assert observed['sslrootcert'] == 'system'
    assert stub.calls[-1] == ("select set_config('gtm.owner_id', %s, true)", (str(owner),))


def test_privileged_login_is_rejected(monkeypatch):
    monkeypatch.setenv('WORKER_DATABASE_URL', 'synthetic')
    monkeypatch.setattr(psycopg, 'connect', lambda *a, **k: ConnectionStub(privileged=True))
    with pytest.raises(PersistenceUnavailable, match='unsafe_database_role'), connection('gtm_worker'):
        pytest.fail('Privileged connection accepted')


def test_raw_connection_error_is_redacted(monkeypatch):
    def fail(*args, **kwargs):
        raise psycopg.OperationalError('synthetic sensitive connection payload')
    monkeypatch.setenv('DATABASE_URL', 'synthetic')
    monkeypatch.setattr(psycopg, 'connect', fail)
    with pytest.raises(PersistenceUnavailable, match='database_unavailable') as error, \
            connection('gtm_api'):
        pytest.fail('Unexpected connection')
    assert 'sensitive' not in str(error.value)
