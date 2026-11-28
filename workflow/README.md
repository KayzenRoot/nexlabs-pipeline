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

## CD-02 additions

```sh
python -m workflow verify
python -m workflow compile
python -m workflow dry-run --workflow NLE-WF-GOV-03 --tenant tenant-1
```

`WorkflowCommands` is the only mutation boundary. It binds security authorization,
approval, durable nonce and the ledger transition in one transaction. Ledger mutation
primitives are private storage methods. Versioned migrations are in `workflow/migrations.py`;
event/run/command schemas are under `workflow/schemas/`; the deterministic 62-workflow
compiler and per-run DAG are in `workflow/compiler.py`. SQLite remains local/offline,
not a production isolation boundary.

## CD-03 additions

`WorkflowCommands` binds the full persisted resource scope (tenant/project/task/workflow/run)
inside the ledger transaction, validates the canonical workflow/version/activation/gate/risk,
uses state-specific action names, and persists approvals only after effective verification.
Recovery is scoped to the authorized workflow/project/task; outbox, flags, DLQ and lease
operations require revision and, where applicable, lease/fencing.

`workflow/outcomes.py` classifies transaction outcomes; `workflow/schema_validation.py`
validates produced event/run/plan documents against the versioned schemas. `compile_run`
emits `nexlabs.workflow-plan.v1`; persisted runs use the expanded `run-v1.json` contract.
SQLite remains local/offline and is not a production isolation boundary.
