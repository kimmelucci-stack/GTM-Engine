"""Fail closed on likely credentials, without printing their values.

Checks Git's staged blobs by default, or every tracked blob in CI with --tracked.
This is a heuristic guard, not a guarantee that every possible secret is detectable.
"""

import argparse
import re
import subprocess
import sys
from pathlib import PurePosixPath

PATTERNS = {
    "provider token": re.compile(
        rb"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
        rb"|sk-(?:proj-)?[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}"
        rb"|xox[baprs]-[A-Za-z0-9-]{20,})"
    ),
    "private key": re.compile(rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"),
    "credential in URL": re.compile(rb"[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@"),
    "JWT": re.compile(rb"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "literal credential assignment": re.compile(
        rb"(?im)^[ \t]*[\"']?(?:[A-Z0-9_]*(?:API_KEY|ACCESS_TOKEN|AUTH_TOKEN|PASSWORD|"
        rb"CLIENT_SECRET|SERVICE_ROLE_KEY|DATAFORSEO_LOGIN|DATABASE_URL))[\"']?"
        rb"[ \t]*[:=][ \t]*[\"']?[^\s\"'#;,\r\n][^\r\n]*"
    ),
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL)


def findings(path: str, data: bytes) -> list[str]:
    file = PurePosixPath(path)
    reasons = []
    if (
        (file.name.startswith(".env") and file.name != ".env.example")
        or file.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
        or file.name in {"credentials.json", ".netrc", ".npmrc"}
        or any(part in {".aws", ".ssh", "secrets"} for part in file.parts)
        or file.name.startswith("service-account")
        or file.name.startswith("credentials.")
    ):
        reasons.append("sensitive file")
    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(data):
            # A SecretStr annotation declares a protected field, not a stored credential.
            # Only a complete annotation with no assignment/comment is exempt.
            if label == "literal credential assignment" and file.suffix == ".py" and re.fullmatch(
                rb"[ \t]*[A-Za-z_][A-Za-z0-9_]*[ \t]*:[ \t]*SecretStr[ \t]*", match.group()
            ):
                continue
            reasons.append(label)
            break
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracked", action="store_true")
    parser.add_argument("--history", action="store_true", help="Also scan all reachable commits")
    args = parser.parse_args()
    try:
        paths = git("ls-files", "-z") if args.tracked else git(
            "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"
        )
        rejected = 0
        for raw_path in paths.split(b"\0"):
            if not raw_path:
                continue
            path = raw_path.decode("utf-8")
            # Always inspect the exact index blob that would be committed.
            for reason in findings(path, git("show", f":{path}")):
                print(f"BLOCKED: {path} ({reason}; value withheld)")
                rejected += 1
        if args.history:
            checked = set()
            commits = git("rev-list", "--all").decode().splitlines()
            for commit in commits:
                for entry in git("ls-tree", "-r", "-z", commit).split(b"\0"):
                    if not entry:
                        continue
                    metadata, raw_path = entry.split(b"\t", 1)
                    _, kind, oid = metadata.split()
                    if kind != b"blob":
                        continue
                    path = raw_path.decode("utf-8")
                    identity = (path, oid)
                    if identity in checked:
                        continue
                    checked.add(identity)
                    for reason in findings(path, git("cat-file", "blob", oid.decode())):
                        print(f"BLOCKED history: {path} ({reason}; value withheld)")
                        rejected += 1
            print(f"History checked: {len(commits)} commits, {len(checked)} distinct file blobs.")
        if rejected:
            print("Secret check failed. Remove credentials before committing.")
            return 1
        print("Secret check passed: no matching credentials in scanned Git blobs.")
        return 0
    except (subprocess.CalledProcessError, UnicodeError):
        print("Secret check could not complete; commit blocked.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
