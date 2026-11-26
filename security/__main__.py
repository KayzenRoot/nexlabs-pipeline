"""Run offline security-contract preflight."""
from .core import verify


def main() -> int:
    try:
        verify()
    except (OSError, ValueError, TypeError) as exc:
        print("SECURITY_CONTRACTS_REJECTED " + type(exc).__name__)
        return 1
    print("SECURITY_CONTRACTS_OK default_deny=true network=offline secrets=opaque")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
