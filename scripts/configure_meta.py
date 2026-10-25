"""Configure Meta locally with hidden input; never accept secrets as arguments."""

import json
import re
import subprocess
import sys
from getpass import getpass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if not sys.stdin.isatty():
        print("Use a local interactive terminal with hidden input.")
        return 2
    ignored = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=ROOT,
                             capture_output=True, check=False)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"], cwd=ROOT,
                             capture_output=True, check=False)
    if ignored.returncode != 0 or tracked.returncode == 0:
        print("Unsafe local configuration; nothing written.")
        return 2
    settings = {name: getpass(f"{name} (hidden): ").strip() for name in
                ("META_ACCESS_TOKEN", "META_APP_ID", "META_IG_USER_ID", "META_GRAPH_API_VERSION")}
    valid = all(v and not any(c in v for c in "\r\n\0") for v in settings.values())
    valid = valid and all(re.fullmatch(r"[0-9]+", settings[k])
                          for k in ("META_APP_ID", "META_IG_USER_ID"))
    valid = valid and re.fullmatch(r"v[0-9]+\.[0-9]+", settings["META_GRAPH_API_VERSION"])
    if not valid:
        print("Invalid input; no values displayed or written.")
        return 2
    target = ROOT / ".env"
    lines = target.read_text(encoding="utf-8-sig").splitlines() if target.exists() else []
    kept = [line for line in lines if line.partition("=")[0].strip() not in settings]
    target.write_text("\n".join(kept + [f"{key}={json.dumps(value)}"
                                      for key, value in settings.items()]) + "\n", encoding="utf-8")
    target.chmod(0o600)
    print("Saved locally. Values withheld. No API calls or permission verification performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
