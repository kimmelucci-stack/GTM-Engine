"""Offline Meta readiness check. Never prints values or makes API requests."""

import argparse
import json
import os
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NAMES = ("META_ACCESS_TOKEN", "META_APP_ID", "META_IG_USER_ID", "META_GRAPH_API_VERSION")


def readiness(root: Path = ROOT, environment=None) -> dict:
    environment = os.environ if environment is None else environment
    values = {}
    reason = None
    target = root / ".env"
    if target.exists():
        ignored = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=root,
                                 capture_output=True, check=False)
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", ".env"], cwd=root,
                                 capture_output=True, check=False)
        if ignored.returncode != 0 or tracked.returncode == 0:
            reason = "local_env_not_protected"
        else:
            try:
                for line in target.read_text(encoding="utf-8-sig").splitlines():
                    key, sep, raw = line.partition("=")
                    if sep and key.strip() in NAMES:
                        value = raw.strip()
                        if value.startswith('"'):
                            value = json.loads(value)
                        elif len(value) >= 2 and value[0] == value[-1] == "'":
                            value = value[1:-1]
                        if not isinstance(value, str):
                            raise ValueError
                        values[key.strip()] = value
            except (ValueError, OSError):
                reason = "invalid_local_settings_values_withheld"
    for name in NAMES:
        if environment.get(name):
            values[name] = environment[name]
    missing = [name for name in NAMES if not values.get(name, "").strip()]
    invalid = []
    for name in ("META_APP_ID", "META_IG_USER_ID"):
        if values.get(name) and not re.fullmatch(r"[0-9]+", values[name]):
            invalid.append(name)
    version = values.get("META_GRAPH_API_VERSION")
    if version and not re.fullmatch(r"v[0-9]+\.[0-9]+", version):
        invalid.append("META_GRAPH_API_VERSION")
    return {
        "version": "gate1c-preflight-v1", "checked_at": datetime.now(UTC).isoformat(),
        "gate_status": "NOT_TESTED", "readiness": "needs_configuration"
        if missing or invalid or reason else "configuration_present_access_unverified",
        "missing_settings": missing, "invalid_setting_names": invalid,
        "configuration_error": reason, "network_requests": 0,
        "provider_access": {"ads_archive": "not_tested", "business_discovery": "not_tested"},
        "limitations": ["Presence is not token validity or permission verification.",
                        "API version must be checked against current official documentation.",
                        "Two advertiser identities and two professional Instagram accounts still required.",
                        "No fallback enabled; no provider spend."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = readiness()
    if args.output:
        output = args.output.resolve()
        ignored = subprocess.run(["git", "check-ignore", "-q", str(output / "report.json")],
                                 cwd=ROOT, capture_output=True, check=False)
        if ignored.returncode != 0:
            parser.error("Output must be ignored by Git")
        output.mkdir(parents=True, exist_ok=False)
        (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
