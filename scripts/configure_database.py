"""Provision separate server logins using hidden administrative input, never CLI secrets."""

import json
import os
import secrets
import subprocess
import sys
import tempfile
from getpass import getpass
from pathlib import Path
from urllib.parse import urlsplit

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

ROOT = Path(__file__).resolve().parents[1]


def configure(administrative: str, auth_url: str, public_key: str) -> int:
    ignored = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=ROOT,
                             capture_output=True, check=False)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"], cwd=ROOT,
                             capture_output=True, check=False)
    if ignored.returncode != 0 or tracked.returncode == 0:
        print("Local settings are not protected. Nothing changed.")
        return 2
    target = ROOT / ".env"
    lines = target.read_text(encoding="utf-8-sig").splitlines() if target.exists() else []
    # Refuse to replace an existing connection or rotate an existing login silently.
    for line in lines:
        name, sep, value = line.partition("=")
        if (sep and name.strip() in {"DATABASE_URL", "WORKER_DATABASE_URL"}
                and value.strip() not in {"", '""', "''"}):
            print("Database settings already exist. Nothing changed.")
            return 2
    if (not auth_url.startswith("https://") or not public_key.startswith("sb_publishable_")
            or any(c in administrative + auth_url + public_key for c in "\r\n\0")):
        print("Invalid configuration. Values withheld; nothing changed.")
        return 2
    staged = None
    committed = False
    try:
        parsed = conninfo_to_dict(administrative)
        # Retain only network coordinates, never administrative options or credentials.
        coordinates = {key: parsed[key] for key in ("host", "port", "dbname") if key in parsed}
        if not coordinates.get("host") or not coordinates.get("dbname"):
            raise ValueError("missing_coordinates")
        auth_host = urlsplit(auth_url).hostname or ""
        if not auth_host.endswith(".supabase.co") or urlsplit(auth_url).path not in {"", "/"}:
            raise ValueError("invalid_auth_host")
        reference = auth_host.removesuffix(".supabase.co")
        if (coordinates["host"] != "db." + auth_host
                and (not coordinates["host"].endswith(".pooler.supabase.com")
                     or parsed.get("user", "").partition(".")[2] != reference)):
            raise ValueError("mismatched_project")
        settings = {"SUPABASE_URL": auth_url, "SUPABASE_PUBLISHABLE_KEY": public_key}
        with psycopg.connect(administrative, connect_timeout=10, sslmode="verify-full",
                             sslrootcert="system") as conn:
            if not conn.execute("select to_regclass('gtm.jobs') is not null").fetchone()[0]:
                raise ValueError("wrong_project")
            for role, variable in (("gtm_api", "DATABASE_URL"),
                                   ("gtm_worker", "WORKER_DATABASE_URL")):
                login = role + "_login"
                if conn.execute("select 1 from pg_roles where rolname=%s", (login,)).fetchone():
                    raise ValueError("existing_login")
                generated = secrets.token_urlsafe(48)
                conn.execute(sql.SQL(
                    "create role {} login noinherit nosuperuser nobypassrls password {}"
                ).format(sql.Identifier(login), sql.Literal(generated)))
                conn.execute(sql.SQL("grant {} to {}").format(
                    sql.Identifier(role), sql.Identifier(login)))
                # Session pooler usernames include the project suffix; direct DB usernames do not.
                suffix = parsed.get("user", "").partition(".")[2]
                username = login + ("." + suffix if suffix else "")
                settings[variable] = make_conninfo(**coordinates, user=username, password=generated)
            kept = [line for line in lines if line.partition("=")[0].strip() not in settings]
            descriptor, staged = tempfile.mkstemp(prefix=".env.provision-", dir=ROOT)
            with os.fdopen(descriptor, "w", encoding="utf-8") as output:
                output.write("\n".join(kept + [f"{k}={json.dumps(v)}"
                                             for k, v in settings.items()]) + "\n")
            Path(staged).chmod(0o600)
        committed = True
        os.replace(staged, target)
        staged = None
    except (psycopg.Error, ValueError, OSError):
        print("Configuration incomplete. Values withheld. No connection test claimed.")
        if committed:
            print("Logins exist; preserve the ignored .env.provision file for recovery.")
        return 2
    finally:
        if staged is not None and not committed:
            Path(staged).unlink(missing_ok=True)
    print("Separate server logins saved locally. Administrative credential not saved.")
    print("Runtime TLS/authentication still need a real connection test. No deployment performed.")
    return 0


def main() -> int:
    if not sys.stdin.isatty():
        print("Use an interactive local terminal. No secrets accepted as arguments.")
        return 2
    administrative = getpass("Dedicated project's administrative connection URL (hidden): ").strip()
    auth_url = getpass("Dedicated project's Supabase HTTPS URL (hidden): ").strip()
    public_key = getpass("Publishable key (hidden): ").strip()
    return configure(administrative, auth_url, public_key)


if __name__ == "__main__":
    raise SystemExit(main())
