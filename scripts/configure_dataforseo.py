"""Local terminal setup with hidden fields. Never accept credentials as CLI arguments."""

import json
import subprocess
import sys
from decimal import Decimal
from getpass import getpass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAP = Decimal(5)  # Explicit pilot authorization from the owner; not a tariff estimate.


def main() -> int:
    if not sys.stdin.isatty():
        print("Open a local interactive terminal; credentials must not be echoed.")
        return 2
    ignored = subprocess.run(["git", "check-ignore", "-q", ".env"],
                             cwd=ROOT, capture_output=True, check=False)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"],
                             cwd=ROOT, capture_output=True, check=False)
    if ignored.returncode != 0 or tracked.returncode == 0:
        print("Unsafe environment file configuration; no credentials written.")
        return 2
    login, password = (
        getpass("DataForSEO API login (hidden): "),
        getpass("DataForSEO API password (hidden): "),
    )
    if not login or not password or any(c in login + password for c in "\r\n\0"):
        print("Invalid input; no values shown or written.")
        return 2
    settings = dict(zip(
        ["DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD", "DATAFORSEO_COST_CAP_USD"],
        [login, password, str(CAP)], strict=True,
    ))
    target = ROOT / ".env"
    existing = target.read_text(encoding="utf-8-sig").splitlines() if target.exists() else []
    kept = [line for line in existing if line.partition("=")[0].strip() not in settings]
    target.write_text("\n".join(kept + [f"{key}={json.dumps(value)}"
                                       for key, value in settings.items()]) + "\n", encoding="utf-8")
    target.chmod(0o600)
    print("Private local settings saved; pilot cap 5 USD. No API requests made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
