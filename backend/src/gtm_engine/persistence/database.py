"""Short-lived TLS connections; credentials and raw errors never leave this boundary."""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from importlib.resources import files
from typing import Literal
from uuid import UUID

import psycopg
from psycopg import sql
from psycopg.rows import dict_row


class PersistenceUnavailable(Exception):
    """Safe public error, deliberately without connection details."""


def tls_options() -> dict[str, str]:
    """Supabase's published root CA, with certificate and hostname verification."""
    root = files("gtm_engine.persistence").joinpath("certs/supabase-root-2021.crt")
    return {"sslmode": "verify-full", "sslrootcert": str(root)}


@contextmanager
def connection(role: Literal["gtm_api", "gtm_worker"], owner_id: UUID | None = None
               ) -> Iterator[psycopg.Connection]:
    variable = "WORKER_DATABASE_URL" if role == "gtm_worker" else "DATABASE_URL"
    dsn = os.environ.get(variable)
    if not dsn:
        raise PersistenceUnavailable("database_not_configured")
    try:
        with psycopg.connect(dsn, connect_timeout=10, **tls_options(), row_factory=dict_row) as conn:
            conn.isolation_level = psycopg.IsolationLevel.READ_COMMITTED
            login = conn.execute(
                "select rolsuper, rolbypassrls from pg_roles where rolname = session_user"
            ).fetchone()
            if not login or login["rolsuper"] or login["rolbypassrls"]:
                raise PersistenceUnavailable("unsafe_database_role")
            conn.execute(sql.SQL("set local role {}").format(sql.Identifier(role)))
            conn.execute("set local statement_timeout = '10s'")
            conn.execute("set local idle_in_transaction_session_timeout = '15s'")
            if owner_id is not None:
                conn.execute("select set_config('gtm.owner_id', %s, true)", (str(owner_id),))
            yield conn
    except psycopg.Error:
        raise PersistenceUnavailable("database_unavailable") from None
