"""Gate 0 worker entry point. Persistent jobs belong to Gate 2."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify the entry point only")
    args = parser.parse_args()
    if not args.check:
        parser.error("Persistent worker not implemented: requires Gate 2")
    print("Worker entry point OK; no jobs executed; persistence not implemented.")


if __name__ == "__main__":
    main()
