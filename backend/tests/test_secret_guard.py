import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "secret_guard", Path(__file__).resolve().parents[2] / "scripts" / "check_secrets.py"
)
assert spec and spec.loader
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def test_empty_env_template_is_allowed() -> None:
    assert guard.findings(".env.example", b"OPENAI_API_KEY=\nDATAFORSEO_LOGIN=\n") == []


def test_nonempty_provider_credentials_are_blocked() -> None:
    for field in ["OPENAI_API_KEY", "DATAFORSEO_LOGIN", "META_ACCESS_TOKEN", "DATABASE_URL"]:
        assert guard.findings("config.txt", f"{field}=synthetic-test-value".encode())


def test_known_token_in_prose_is_blocked() -> None:
    assert guard.findings("notes.md", ("token: " + "ghp_" + "a" * 36).encode())


def test_sensitive_files_are_blocked_even_when_empty() -> None:
    for path in [".env", "backend/.env.production", "key.pem", ".aws/credentials"]:
        assert guard.findings(path, b"")
