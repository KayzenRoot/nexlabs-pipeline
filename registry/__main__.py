"""CLI emits deterministic local JSON or validates a saved dry-run artifact."""
import argparse
import sys
from pathlib import Path

from .core import build, canonical_bytes, provision_plan, read_json, verify_document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="validate source pack and compile both documents")
    commands.add_parser("build", help="emit candidate registry and agent locks")
    commands.add_parser("plan", help="emit disabled, offline provision intentions")
    validate = commands.add_parser("validate", help="verify a previously emitted JSON")
    validate.add_argument("document", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "verify":
            bundle = build()
            plan = provision_plan(bundle=bundle)
            print("REGISTRY_OK agents=%d packages=%d assignments=%d intents=%d runtime_writes=0"
                  % (bundle["summary"]["agents"], bundle["summary"]["packages"],
                     bundle["summary"]["assignments"], len(plan["agent_intents"])))
        elif args.command == "validate":
            verify_document(read_json(args.document))
            print("REGISTRY_DOCUMENT_OK")
        else:
            document = build() if args.command == "build" else provision_plan()
            sys.stdout.buffer.write(canonical_bytes(document))
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as exc:
        # Do not print arbitrary input, paths or exception details from candidate files.
        print("REGISTRY_REJECTED " + type(exc).__name__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
