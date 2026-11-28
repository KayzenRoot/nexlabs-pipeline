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

## HIGH_ASSURANCE Correction Delta CD-02 | 2026-11-27

A auditoria oficial no HEAD `82180fa4c9a29fc735ecb492c1e497bc75d0d53a` emitiu CORRECTION REQUIRED com F01–F06. Correções no mesmo Work Order/PR:

- **F01:** `WorkflowCommands` é a única fronteira pública de mutação; autorização security.authorization/approval, nonce, mutação e transição na mesma transação; Ledger expõe apenas leitura e primitivas privadas; payload assinado deriva dos parâmetros do comando e de `policy_epoch`; risco de evento não pode ser rebaixado; `APPROVED → VERIFIED → COMPLETED`.
- **F02:** tenant/project/task/workflow/risk no run; FKs compostas; referências de event/run/outbox/DLQ/approval validadas; append com run existente do mesmo tenant; revisão obrigatória; colisão de idempotência/payload rejeitada; outbox bloqueado em run terminal ou BLOCKED; SQL parametrizado; WAL obrigatório sem fallback silencioso; integrity/FK check; SQLite explicitamente local.
- **F03:** nonce exige expiração futura, retenção de 24h, replay/rollback/atomicidade; aprovação persistida com escopo completo, incluindo approver_role/evidence_refs/max_spend/issued_at; `run_id` nullable para append/recovery; migração v3 transacional, resiliente a legado/parcial/retomada; schema v6 resumível com backfill fail-closed de risco (ausente/não-string/lista/objeto/inválido vira HIGH_ASSURANCE); rollback remove nonce/aprovação; HMAC test-only.
- **F04:** recovery libera lease expirada, incrementa attempts/revision e aplica cap sem exceder 2; lease ativa preservada; fencing obrigatório em RUNNING/EFFECT_IN_PROGRESS; EFFECT_IN_PROGRESS pode ser claimado e verificado; stale/revogado/deadline expirado nunca retorna a retry; BLOCKED tem saídas definidas; UNKNOWN_EFFECT exige `reconciliation_ref`; deadline/TTL; 429/5xx cap 2 consistente com o ledger.
- **F05:** RunContract com risk, schemas versionados e conferidos contra contratos, migrações v4 transacionais/resumíveis com backfill de risco fail-closed, 62-workflow compiler com summary/grants derivados, DAG/validate_dag, CLI verify/compile/dry-run, source lock/deadline/stale/revogação irreversível e approval persistida restaurados.
- **F06:** Context Lock verifica base tree, ancestralidade, `origin/main` obrigatório, drift/worktree de fontes e implementação, canônicos no base e HEAD, conjuntos 24 canônicos + 17 de implementação e 364 fontes; C12 usa allowlist no workflow/steps e varredura recursiva de campos aninhados de privilégio/memória/skill/client; zero grants é verificado nos 62 workflows.

## Acceptance Criteria CD-02

AC01 Context Lock/base/364/fingerprints; AC02 Event Contract; AC03 Run/ledger/migrações/imutabilidade; AC04 estados e APPROVED→VERIFIED→COMPLETED; AC05 command boundary/deny-by-default; AC06 approval/nonce/replay/rollback offline; AC07 atomicidade; AC08 concorrência/lease/fencing; AC09 recovery/retry/reconciliação; AC10 outbox/DLQ; AC11 C12 canônico; AC12 retry/limites; AC13 CLI verify/compile/dry-run; AC14 CI/auditoria. Status local: AC01–AC13 PASS em 156/156 testes; AC14 PENDING final HEAD.

**Não declarar o Work Order pai completo enquanto a auditoria independente CD-02 e os gates remotos não estiverem APPROVED.** Sem merge, checkpoint, VPS, Paperclip runtime, segredos, agentes, workflows, modelo ou despesa.

## HIGH_ASSURANCE CD-03 — Reconciliation | 2026-11-28

Auditoria CD-03 no HEAD `1e61917` emitiu CORRECTION REQUIRED com F01-R1–F07. Correções no mesmo Work Order/PR:

- **F01-R1:** binding completo tenant/project/task/workflow/run/actor/action/target/risk dentro da transação; recovery filtrado pelo escopo; testes cross-project/task/workflow.
- **F01-R2:** validação canônica de workflow/version/activation/gate/risk/segregação; autorização por operação e estado; HUMAN_APPROVAL_REQUIRED e C12; aprovação verificada; authorizer substituível removido; DISABLED sem efeitos.
- **F02/F04-R3:** outbox com revisão/stale/revoked/deadline/lease; flags com revision e audit_events; DLQ com revisão/auditoria; claim com revisão e lease expirada exigindo recovery.
- **F03/F04-R4:** ownership transacional por thread/instância; migrações v3/v4/v5 transacionais e resumíveis; classificação COMMITTED/REPLAY_REJECTED/CONFLICT/STORAGE_ERROR; testes multiprocesso, crash, rollback e migração interrompida.
- **F05:** RunContract completo conforme README original; DDL/schema/migração/compilador reconciliados; skill_lock/model/quota/refs/status/gate; validação real de event/run/plan contra JSON Schemas.
- **F06:** conjuntos exatos de 24 paths canônicos + 21 de implementação; integridade antes de verify/compile/c12/dry-run; lock CD-03; 364 fontes, 62 workflows e C12 preservados.
- **F07:** auditoria independente pendente no HEAD final.

Status local: AC01–AC13 PASS em 185/185 testes; AC14 PENDING. Sem merge, checkpoint, VPS, Paperclip runtime, segredos, agentes, workflows ativos, modelo, efeitos externos ou despesa.
