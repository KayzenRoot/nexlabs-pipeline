# NLE-WF-WO-001/CD-01 — Event, authorization and ledger contracts

**Classification:** NECESSARY
**Risk:** HIGH_ASSURANCE
**Parent:** NLE-WF-WO-001 (event, authorization and ledger)
**Base:** `04724af867659e278210489c8ba91fc6344e3fb1`
**Mode:** OFFLINE_CONTRACT_ONLY — no runtime activation

## OBJECTIVE

Recover and publish the offline workflow-control slice: strict event envelopes, a durable append-only SQLite ledger, state machine, deny-by-default authorization using the approved security contracts, durable approval nonce/replay protection, lease fencing, crash recovery, outbox/DLQ and the C12 dispatch-only contract for the five affected workflows.

## SCOPE

- Standard-library-only Python package `workflow/`.
- Event envelope validation, canonical hash and idempotency.
- SQLite ledger with WAL, full synchronous writes, append-only event triggers, transactional run/event/outbox writes.
- State machine with explicit transitions and terminal states.
- Reuse of `security.authorization` for exact-scope workflow authorization and `security.approval` for HIGH_ASSURANCE approval.
- Durable nonce consumption; concurrency and lease fencing; recovery from expired leases and unknown effects.
- C12 validation for `NLE-WF-GOV-03`, `NLE-WF-QNT-01`, `NLE-WF-QNT-02`, `NLE-WF-QNT-03`, `NLE-WF-QNT-05`.
- Tests, CLI, Work Order, Context Lock and Evidence Bundle.

## OUT OF SCOPE

Paperclip API/DB writes, dispatcher execution, workflow/agent/routine activation, live network, WireGuard, VPS/SSH, secrets or credential resolution, model calls, production effect delivery, merge, checkpoint promotion and any spend.

## ACCEPTANCE CRITERIA

- **AC01:** Context Lock captures the real base tree `d0f135f2…`, 364 Source Pack files and zero canonical/implementation fingerprint divergence; approved implementation is preserved.
- **AC02:** Event envelope rejects unknown types, invalid IDs, non-UTC or reversed timestamps, non-SHA-256 payloads, unsafe payload references and unknown risk/classification.
- **AC03:** Event ledger is durable and append-only: unique event/idempotency keys, immutable events (UPDATE/DELETE fail), WAL and integrity check.
- **AC04:** State machine permits only declared transitions, rejects invalid/terminal transitions and records each transition with revision.
- **AC05:** Workflow authorization is deny-by-default, exact-scope and zero-spend/external-effect using the approved security contracts.
- **AC06:** HIGH_ASSURANCE approval is bound to the full request scope; durable nonce is single-use across process restart; replay and self-approval deny. Offline verification uses the security package's test-only HMAC adapter; real human identity and production key custody remain an explicit later production gate and are not claimed by this CD.
- **AC07:** Run creation is atomic with its event and transition; duplicate event/idempotency produces no second run or partial row.
- **AC08:** Concurrent writers yield exactly one winner for the same idempotency/run; distinct events all commit; lease ownership and fencing reject stale writers.
- **AC09:** Recovery converts expired RUNNING leases to RETRY_WAIT and EFFECT_IN_PROGRESS to UNKNOWN_EFFECT without blind retry; no automatic effect delivery.
- **AC10:** Outbox uniqueness, DLQ sanitized references and terminal/quarantine behavior are enforced; no external effect is implemented.
- **AC11:** C12 output contains exactly the five dispatch-only workflows; dispatcher is never executor, accountable or reviewer; no skill, memory or client grants; all remain DISABLED.
- **AC12:** Retry policy blocks 401/403, respects 429 Retry-After, caps attempts at 2 and never retries unknown effects; spend remains 0.
- **AC13:** `python -m workflow verify` validates source lock, catalog/C12 and a durable ledger smoke test deterministically.
- **AC14:** Full canonical suite/validators on Linux; security and workflow suites plus `workflow verify` on Windows; SonarCloud, Socket and ECC pass; independent HIGH_ASSURANCE audit APPROVED on the exact HEAD; no runtime activation or spend.

## TESTS

```text
python -m unittest discover -s tests -v
python scripts/validate_sources.py
python -m registry verify
python -m security verify
python -m workflow verify
python scripts/security/scan_repository.py
```

## STOP CONDITIONS

Any HIGH/CRITICAL finding, failed check, source drift, stale Context Lock, secret exposure, real network/VPS/runtime write, agent/workflow activation, additional spend or missing independent audit blocks merge and the next Work Order.

## DELIVERABLES

Workflow package, schemas/contracts, tests, CLI, Work Order, Context Lock, Evidence Bundle and draft PR. No merge, checkpoint promotion, VPS, secrets, agents, models or spend.
