# NLE-WF-WO-001/CD-03 — Reconciliation and Evidence

Data: 2026-11-28
Repositório: `KayzenRoot/nexlabs-pipeline`
PR: #10 (draft, branch `work/nle-wf-wo-001`)
Base: `04724af867659e278210489c8ba91fc6344e3fb1`
HEAD CD-02 auditado: `1e6191729d8c6ddad1f3779999972d8e7a10853e`
Status: **CANDIDATE_PENDING_CD03_INDEPENDENT_AUDIT**

## 1. Preflight e reconciliação

- Working tree inicial limpo.
- HEAD local = `origin/work/nle-wf-wo-001` = `1e61917`; nenhum commit CD-03 local não publicado.
- `origin/main` permanece na base `04724af`.
- PR #10 permanece OPEN/DRAFT.
- Auditoria CD-03: `CORRECTION REQUIRED`, findings F01-R1–F07.
- 364 fontes preservadas; WF-ADR-001..005 permanecem PROPOSED.

## 2. Correções F01–F07

### F01-R1 — resource scope

- `WorkflowCommands._require_run_scope` compara tenant, project, task e workflow persistidos contra `CommandScope` e aplica o piso de risco.
- `Ledger.run_scoped` e as primitivas sensíveis recebem o escopo dentro da transação.
- Recovery filtra por tenant/project/task/workflow; não opera em todo o tenant.
- Testes negativos cross-project, cross-task e cross-workflow no mesmo tenant; nenhum registro é alterado.

### F01-R2 — gates canônicos e aprovação

- `WorkflowCommands` valida workflow canônico: existência, versão `0.1.0`, activation DISABLED, gate, risk, segregação reviewer/accountable/executor e C12.
- Ações de autorização incluem operação e estado (`workflow.run.transition.<from>.<to>`, lease/outbox/DLQ/flags/reconcile por estado).
- `HUMAN_APPROVAL_REQUIRED` exige HIGH_ASSURANCE e aprovação independente verificada.
- `authorizer` substituível foi removido; o boundary usa `authorize_workflow`.
- Aprovação só é persistida quando efetivamente verificada; aprovação fornecida em risco inferior é negada com rollback.
- Transições para EFFECT_READY/EFFECT_IN_PROGRESS são negadas no boundary porque todos os workflows estão DISABLED.

### F02/F04-R3 — mutações e invariantes

- Outbox exige revisão, escopo, stale/revoked/deadline, estado permitido e lease/fencing quando executor.
- Flags exigem revisão, incrementam revision e gravam `audit_events`.
- DLQ exige revisão, escopo e grava auditoria.
- Claim exige revisão; lease expirada não pode ser reclamada diretamente e exige recovery.
- `UNKNOWN_EFFECT` mantém reconciliação obrigatória e ausência de retry cego.

### F03/F04-R4 — ownership e concorrência

- `Ledger._transaction` usa RLock por instância e ownership de thread; thread estranha não entra em transação alheia.
- Leituras públicas são serializadas pelo mesmo lock.
- Migrações 3/4/5 são transacionais; v3 detecta tabela nova/parcial/rename; v4/v5 são resumíveis; v5 adiciona Run Contract completo e `audit_events`; v6 adiciona `actor_id` em audit_events e `actor_id/action` em transitions de forma resumível.
- Migração falha fechada sem registrar versão incompleta quando approvals falta e approvals_v3 é incompleta.
- Testes: mesma instância/threads, conexões independentes, processos independentes, nonce multiprocesso, crash dentro de transação, rollback após nonce, falha de registro de aprovação, revisão concorrente, reopen, `integrity_check` e `foreign_key_check`.
- `_consume_outcome` classifica `COMMITTED`, `REPLAY_REJECTED`, `CONFLICT` e `STORAGE_ERROR`; erro SQLite não é convertido em replay.

### F05 — Run Contract completo

- `RunContract` e schema `run-v1.json` incluem: workflow/version, run, correlation, event, tenant, project, task, idempotency_key, source_lock, agent_id, skill_lock(id/version/hash), model_id, quota, data_classification, risk, inputs_ref, output_ref, evidence_ref, deadline, approval_ref, status, gate, activation.
- DDL/migração v5 preenchem os campos; valores não qualificados permanecem `null` ou `0`, sem inventar modelo/skill/evidência.
- `status` é sincronizado com o estado; `deadline`, revisão, attempts, lease e flags continuam persistidos.
- `compiler.compile_run` emite `nexlabs.workflow-plan.v1` distinto do schema persistido, preservando step, agent, task, scope, autonomy_ceiling, eligible_packages e efeito DENY.
- Documentos event/run/plan são validados contra seus JSON Schemas por validador fail-closed próprio, sem dependência externa.

### F06 — Context Lock e C12

- `verify_context_lock` exige conjuntos exatos de 24 paths canônicos e 21 de implementação (não apenas contagens), SHA-256 e Git blob; valida base/árvore/ancestralidade/origin main, source lock 364 e drift de fontes/implementação.
- CLI `verify`, `compile`, `c12` e `dry-run` validam source/context lock antes de consumir fontes.
- 62 workflows preservados: 36 INTERNAL_ONLY, 12 POLICY_GATED_EXTERNAL, 14 HUMAN_APPROVAL_REQUIRED, todos DISABLED.
- C12 restrito a GOV-03/QNT-01/02/03/05; dispatcher NLE-ATHENA-PMO; zero grants/memória/skills/client; allowlist e varredura recursiva.

## 3. Testes

| Verificação | Resultado |
|---|---|
| Suíte local | **195/195 OK** |
| Baseline CD-02 | 156/156 OK |
| Novos testes CD-03 | 39 |
| `workflow verify` | PASS local |
| Source Pack | 7/7; 364 fontes |
| Registry | 105/92/1110; 0 writes |
| Security verify | PASS |
| Scanner | 497 arquivos, 0 achados |
| CLI compile/c12/dry-run | PASS local, com integrity gate |

## 4. CI e segurança

- Correction Delta 02: code head `53c2ca017be7b9b279954e9d5ac1c05e29a2e5ef` run **46151975227** e docs head `24fde2c3afdf5f07aba2ab1b2e437e65cd14117d` run **46152110904** — ambos SUCCESS (Linux 187 testes + Windows); Sonar 0; Socket/ECC PASS.
- Correction Delta 03, code head `28059123ef4e7d9f4bacd37cabe28aa209018ced`: run **46158146428** — falha esperada e exclusivamente nos quatro gate-tests do Context Lock (`CONTEXT_LOCK_IMPLEMENTATION_MISMATCH`, lock anterior ainda vinculado ao HEAD anterior); os demais 191 testes Linux e 45+24-4 testes Windows passam. Run anterior `d2a2c90` (**46157620690**) teve, além do gate, um `FileNotFoundError` de `SemLock._rebuild` no Linux ao reconstruir `Barrier(1)` do worker de crash — corrigido com ready handshake sem barrier no cenário F.
- O CI do HEAD documental final (commit que contém este lock) é verificado por read-back no SHA exato no GitHub e registrado no corpo da PR e no relatório externo; não é embutido no lock.
- SonarCloud no code head: 0 issues abertas, Quality Gate passed.
- Nenhum ruleset, proteção da main ou gate foi alterado.

## 5. Acceptance Criteria

| AC | Status local |
|---|---|
| AC01 Context Lock/base/364/fingerprints | PASS local; lock CD-03 pendente do commit |
| AC02 Event Contract | PASS |
| AC03 Run Contract/ledger/migrações (v3 integral) | PASS |
| AC04 estados (inclui VERIFIED→QUARANTINED) | PASS |
| AC05 autorização/escopo (primitiva fail-closed) | PASS |
| AC06 aprovação/nonce | PASS offline |
| AC07 atomicidade | PASS |
| AC08 concorrência/leases (multiprocesso sincronizado) | PASS |
| AC09 recovery/retry | PASS |
| AC10 outbox/DLQ (append terminal + invalidação) | PASS |
| AC11 C12 | PASS |
| AC12 retry/limites/deadline | PASS |
| AC13 CLI | PASS local; integrity gate no commit final |
| AC14 CI/auditoria | CI do HEAD final por read-back; auditoria independente pendente |

## 6. Limitações

- SQLite é armazenamento local/offline, não isolamento produtivo.
- HMAC é test-only; identidade humana e custódia de chave são gates de produção.
- Cobertura não medida; sem alegação de cobertura.
- Migrações/crash são testados com bancos sintéticos.
- Auditoria independente CD-03 ainda não executada neste HEAD.

## 7. Checkpoint Delta

Somente propor após auditoria independente APPROVED no HEAD exato. Sem merge, promoção, NLE-WF-WO-002 ou NLE-INFRA-WO-003 nesta execução.

## 8. Correções da auditoria CD-03 no HEAD 798d441

- **HIGH-01:** payload de `workflow.run.create` agora inclui agent_id, skill_lock id/version/hash, model_id, quota, output_ref e evidence_ref; aprovação não pode ser reutilizada com RunOptions diferentes.
- **HIGH-02:** `WorkflowCommands` rejeita accountable executor; QNT-05 é marcado em C12 com `ACCOUNTABLE_EXECUTES`, `runtime_authorized=false` e `execution_allowed=false`, sem alterar as 364 fontes.
- **HIGH-03:** validador de schema aplica `minItems`, date-time com hora/fuso e rejeita keywords não suportadas; testes de nodes vazio e data-only.
- **MEDIUM-01:** `audit_events` registra `actor_id` em claim/flags/DLQ; comandos passam o principal autorizado.
- **MEDIUM-02:** `counts` e `integrity` usam o lock da instância.
- **MEDIUM-03:** `sqlite3.IntegrityError` é classificado como `CONFLICT`, não storage.
- **LOW-01:** CLI captura `SecurityError` e retorna `WORKFLOW_REJECTED`.
- **LOW-03:** skill_lock exige id/version/hash juntos; `quota` exposto no boundary.

## 9. Segunda correção da auditoria CD-03 (HEAD fa1a3b5)

- **HIGH-01:** schema v6 adiciona `audit_events.actor_id` e `transitions.actor_id/action` de forma transacional/resumível; upgrade de uma base v5 sem `actor_id` é testado.
- **MEDIUM-01:** `RunOptions.agent_id` não pode ser reviewer, accountable ou dispatcher; testes negativos para os três papéis.
- **MEDIUM-02:** transições e recovery gravam actor_id e ação autorizada; teste da transição `RECEIVED→VALIDATED`.
- CI passa a executar `python -m workflow c12` como step dedicado.

## 10. Correction Delta 02

- **F01-R1 append scope:** `_append_event` recebe scope completo, valida `run_scoped` na mesma transação e grava actor/action em auditoria; testes cross-project/task/workflow.
- **F02/F04 DLQ/quarentena:** `dead_letter` transiciona atomicamente para QUARANTINED, grava transição, DLQ e auditoria; outbox e retomada são negados; teste de rollback/duplicata.
- **F02/F04 outbox audit:** enqueue grava actor/action na mesma transação; duplicata reverte auditoria.
- **F03/F04 migration v3:** exige conjunto completo de colunas, índices e FK; parcial com quatro campos + run_id falha fechada e não registra versão.
- **F05 schema validator:** tipos e formatos desconhecidos são rejeitados; minItems/pattern/date-time recursivos mantidos.
- **AC08 multiprocesso:** criação concorrente do mesmo run/idempotency, eventos distintos, nonce, lease/fencing e recovery; exitcodes, integridade e FK verificados.

## 11. Correção da oitava auditoria

- **HIGH-01:** `WorkflowCommands.append_event` exige `run_id`; não há mais append público sem escopo/auditoria. Append com run usa `run_scoped` e grava `now` do comando.
- **HIGH-02:** QUARANTINED é transição permitida a partir dos estados não terminais relevantes (QUEUED/RUNNING/REVIEW/APPROVED/WAITING_APPROVAL/CORRECTION_REQUIRED/EFFECT_READY/EFFECT_IN_PROGRESS/UNKNOWN_EFFECT/RETRY_WAIT/STALE/BLOCKED), mantendo outbox e retomada bloqueados.
- **MEDIUM-01:** auditoria de append usa o timestamp da operação (`now`), não `event.received_at`.
- **LOW-01:** branch legado da migração v3 executa `_validate_approvals_v3` ao final.
- **AC08:** testes multiprocesso adicionais para mesmo run/idempotency, eventos distintos, lease/fencing e recovery; exitcodes/integridade/FK.

## 12. Correção da nona auditoria

- **HIGH-01:** `transition` e `reconcile` negam `QUARANTINED`; apenas `dead_letter` efetiva DLQ/quarentena/auditoria. `_transition` também nega o alvo para defesa em profundidade. Teste negativo com grant de transição.
- **LOW-01:** branch legado da migração v3 passa por `_validate_approvals_v3` após a cópia e criação de índices.

## 13. Correction Delta 03 (F07–F13 da décima auditoria)

Auditoria independente HIGH_ASSURANCE no HEAD `24fde2c3afdf5f07aba2ab1b2e437e65cd14117d` (code head `53c2ca0`) emitiu CORRECTION REQUIRED com F07–F13. Correções no mesmo WO/PR, code head `28059123ef4e7d9f4bacd37cabe28aa209018ced`:

- **F07 LOW — Lock/Evidence coerentes:** este Evidence Bundle e o Context Lock registram o code head e o HEAD documental separadamente, o CI real por run/SHA (incluindo os runs 46152110904/46151975227 do Delta 02 e o run 46158146428 do code head Delta 03, com falha esperada apenas no gate de lock) e removem a referência contraditória a auditoria aprovada; `independent_audit` registra o veredito CORRECTION REQUIRED da décima auditoria e o status pendente de reauditoria.
- **F08 HIGH — append em terminal/quarentena:** `commands.append_event` verifica o estado no boundary; `Ledger._append_event` revalida `state not in TERMINAL` (definição centralizada em `contracts.TERMINAL`) dentro da mesma transação; inserção de evento e auditoria permanecem atômicas. Testes: COMPLETED/CANCELLED/QUARANTINED negados, RECEIVED/RUNNING/VERIFIED permitidos, run inexistente e escopo cruzado negados, nenhum evento/auditoria parcial após falha.
- **F09 HIGH — invalidação da outbox na quarentena:** `Ledger._dead_letter` cancela atomicamente todas as mensagens `PENDING` do run (`status=CANCELLED`), grava audit `workflow.outbox.cancel` com actor/timestamp na mesma transação e inclui `outbox_cancelled` na auditoria do DLQ; `enqueue_outbox` já nega runs em `OUTBOX_BLOCKED_STATES` (inclui QUARANTINED); não há caminho de claim/dispatch nesta entrega (a elegibilidade futura é a status CANCELLED + revalidação de estado na fila). Testes: duas pendências canceladas, DLQ/transição/auditoria persistidas, enqueue negado, DLQ duplicado negado, rollback por falha injetada na auditoria não deixa runs/DLQ/transição/outbox/audit parciais.
- **F10 HIGH — migração v3 valida constraints reais:** `_validate_approvals_v3` agora valida, por PRAGMA e sqlite_master, as 23 colunas em ordem com tipo/NOT NULL/default/PK exatos, AUTOINCREMENT na PK, UNIQUE composto `(approval_id, run_id, tenant_id)`, `idx_approvals_run` não-unique com `(run_id, tenant_id)`, `idx_approvals_null_run` unique parcial em `approval_id` com predicado `run_id IS NULL`, FK única `(run_id, tenant_id) → runs(run_id, tenant_id)` na ordem e com ações NO ACTION, e `PRAGMA foreign_key_check`. Fixtures adversariais: índice com nome correto e definição errada (unique/colunas trocadas), índice parcial não-unique e sem predicado, ausência do UNIQUE composto, FK para tabela errada/uma coluna/ordem invertida, tipo e NOT NULL incorretos, PK sem AUTOINCREMENT — todos falham sem registrar versão (rollback integral); schema válido migra. Branch legado preservada.
- **F11 MEDIUM — concorrência sincronizada:** os cinco workers multiprocesso sinalizam READY pela fila e liberam via `multiprocessing.Barrier` compartilhada (timeout 30s); o controlador exige READY de todos antes da contenção, faz join com timeout, encerra órfãos, exige exitcode 0 e coleta resultados estruturados. Cenários: mesmo run/idempotência (um vencedor), eventos distintos (nenhuma perda), nonce (um COMMITTED), lease/fencing (um owner, epoch 1, claim pós-lease negado), recovery (uma transição). Crash/rollback usa READY handshake e encerra dentro da transação; banco recuperável com integrity/FK. Sem `sleep()` como sincronização.
- **F12 MEDIUM — VERIFIED → QUARANTINED:** `TRANSITIONS["VERIFIED"] = {COMPLETED, QUARANTINED}`; QUARANTINED permanece terminal; transição válida apenas via `dead_letter` (DLQ+transição+auditoria+invalidação atômicas); `transition`/`reconcile` genéricos continuam negando QUARANTINED no boundary e em `_transition`. Testes: VERIFIED→QUARANTINED via DLQ PASS; via transition/reconcile genéricos DENY; QUARANTINED→qualquer estado DENY; rollback do DLQ ausente coberto por F09.
- **F13 MEDIUM — scope fail-closed na primitiva:** `_append_event` exige scope completo (3-tupla project/task/workflow) sempre que `run_id` está presente, valida identificadores via `run_scoped` e remove o fallback por run_id+tenant; o caminho sem run permanece para eventos sem execução, conforme contrato interno. Testes diretos na primitiva: escopo correto PASS; ausente/malformado/cruzado (tenant, project, task, workflow) e run inexistente DENY, sem linhas parciais.

Suíte local: 195/195 OK (156 CD-02 + 39 CD-03) no code head. Auditoria independente HIGH_ASSURANCE do HEAD final permanece PENDING.
