"""Start the local API or one worker pass with allowlisted, ignored server settings."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"DATABASE_URL", "WORKER_DATABASE_URL", "SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY",
         "SUPABASE_SERVICE_ROLE_KEY", "SESSION_ENCRYPTION_KEY", "APP_ORIGIN"}


def local_settings(root: Path = ROOT) -> dict[str, str]:
    target = root / ".env"
    if not target.exists():
        return {}
    for command, expected in ((["git", "check-ignore", "-q", ".env"], 0),
                              (["git", "ls-files", "--error-unmatch", ".env"], 1)):
        result = subprocess.run(command, cwd=root, capture_output=True, check=False)
        if result.returncode != expected:
            raise ValueError("local_settings_not_protected")
    values = {}
    for line in target.read_text(encoding="utf-8-sig").splitlines():
        name, sep, raw = line.partition("=")
        if not sep or name.strip() not in NAMES:
            continue
        value = raw.strip()
        if value.startswith('"'):
            value = json.loads(value)
        elif len(value) > 1 and value[0] == value[-1] == "'":
            value = value[1:-1]
        if not isinstance(value, str) or any(c in value for c in "\r\n\0"):
            raise ValueError("invalid_settings")
        if value:
            values[name.strip()] = value
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["check", "api", "worker"])
    parser.add_argument("--poll", action="store_true", help="Continuously process supported worker jobs")
    parser.add_argument("--reload", action="store_true", help="Reload local API when backend source changes")
    args = parser.parse_args()
    if args.mode == "api":
        prepare_session_key()
    try:
        environment = {**os.environ, **{k: v for k, v in local_settings().items()
                                      if not os.environ.get(k)}}
    except (ValueError, OSError):
        print("Local settings unavailable; values withheld.")
        return 2
    required = ({"WORKER_DATABASE_URL"} if args.mode == "worker" else
                {"DATABASE_URL", "SUPABASE_URL", "SUPABASE_PUBLISHABLE_KEY"})
    if args.mode == "check":
        print(json.dumps({name: bool(environment.get(name)) for name in sorted(NAMES)}))
        return 0
    if not all(environment.get(name) for name in required):
        print("Required server settings missing. No service started.")
        return 2
    command = ([sys.executable, "-m", "gtm_engine.worker", "--once"] if args.mode == "worker"
               else [sys.executable, "-m", "uvicorn", "gtm_engine.api:app",
                     "--host", "127.0.0.1", "--port", "8000"])
    if args.mode == "worker" and args.poll:
        command[-1] = "--poll"
    if args.mode == "api" and args.reload:
        command += ["--reload", "--reload-dir", str(ROOT / "backend/src")]
    return subprocess.run(command, cwd=ROOT, env=environment, check=False).returncode


def prepare_session_key() -> None:
    """Generate once in the ignored local settings; never replace an existing key."""
    from cryptography.fernet import Fernet
    if os.environ.get("SESSION_ENCRYPTION_KEY") or local_settings().get("SESSION_ENCRYPTION_KEY"):
        return
    path = ROOT / ".env"
    if not path.is_file():
        raise ValueError("database_setup_required")
    text = path.read_text(encoding="utf-8-sig")
    lines = [line for line in text.splitlines()
             if line.partition("=")[0].strip() != "SESSION_ENCRYPTION_KEY"]
    lines.append("SESSION_ENCRYPTION_KEY=" + json.dumps(Fernet.generate_key().decode()))
    temporary = ROOT / ".env.session.tmp"
    try:
        temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
