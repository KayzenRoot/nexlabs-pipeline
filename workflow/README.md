# Offline workflow controls | NLE-WF-WO-001

This package is an offline workflow contract, not a dispatcher or runtime.

```sh
python -m workflow verify
python -m workflow c12
```

- `workflow/contracts.py` defines strict events, state transitions, retry decisions and C12.
- `workflow/ledger.py` is a durable SQLite ledger: WAL, full synchronous writes, append-only event triggers, unique event/idempotency, nonces, leases, outbox, DLQ and recovery.
- `workflow/authorization.py` reuses the approved exact-scope security authorization and durable nonce store.
- `workflow/__main__.py` performs a deterministic offline verification with a temporary ledger.

No Paperclip API/DB writes, network, WireGuard, VPS/SSH, secrets, agents, workflows, model calls or external effects exist in this package. All workflows remain DISABLED; C12 dispatch is a contract only. Approval and identity providers remain production gates from the security work order.
