# NLE-WF-WO-001/CD-02 — HIGH_ASSURANCE Correction Delta evidence

Data: 2026-11-27
Repositório: `KayzenRoot/nexlabs-pipeline`
PR: #10 (draft, branch `work/nle-wf-wo-001`)
Base: `04724af867659e278210489c8ba91fc6344e3fb1`
Base tree: `d0f135f2ba896a5fe22f21610bae78f025c0650e`
HEAD anterior auditado: `82180fa4c9a29fc735ecb492c1e497bc75d0d53a`
Status: **CANDIDATE_PENDING_CD02_INDEPENDENT_AUDIT**

## 1. Escopo e proveniência

A auditoria oficial do ChatGPT em `82180fa` emitiu **CORRECTION REQUIRED** com F01–F06 HIGH/MEDIUM. Uma segunda auditoria independente em `0122cfc` emitiu **CORRECTION REQUIRED** com C12 allowlist, zero grants global, BLOCKED, migração v3, retry e risco de run. Uma terceira auditoria em `902c02f` emitiu **CORRECTION REQUIRED** com campos C12 aninhados e migração v4/risco legado. Uma quarta auditoria em `a67b459` manteve apenas um MEDIUM: `risk` JSON lista/objeto quebrava `_event_risk` em vez de virar HIGH_ASSURANCE. Esta CD-02 corrige o código no mesmo Work Order, branch e PR #10. Não cria Work Order, não faz merge, não promove checkpoint, não inicia NLE-WF-WO-002/INFRA-WO-003, não acessa VPS/rede/segredos/Paperclip runtime e não gera gasto.

## 2. Correções F01–F06

### F01 — fronteira única de comandos autorizados

- `workflow/commands.py`: `WorkflowCommands` é a única API pública de mutação; o ledger interno é `_ledger`, e Ledger expõe somente leitura e primitivas privadas `_*` (`_conn`, `_transaction`, `_consume`).
- Cada comando usa `security.authorization`/`security.approval`; a transação abrange autorização, nonce, mutação, transição e registro de aprovação.
- O payload assinado é derivado dos parâmetros de cada comando (target, evento, `run_id` de append, versão/deadline de create, revisão, lease, TTL, reason/ref, flags, outcome/evidence) e inclui `policy_epoch`; aprovação não pode ser reaproveitada com parâmetros diferentes.
- Decisão vinculada a principal, tenant, project, task, workflow, target/run, ação, payload, risco e policy; ações desconhecidas, grant ausente/escopo divergente e revisão obsoleta negam.
- Risco do evento não pode ser rebaixado: comando STANDARD não processa evento HIGH_ASSURANCE.
- `APPROVED → VERIFIED → COMPLETED`; `APPROVED → COMPLETED` não existe. Efeitos externos permanecem negados; o ledger é apenas armazenamento offline.

### F02 — integridade, referências e isolamento

- `runs` carrega tenant/project/task/workflow/version/event/correlation/source-lock/deadline/stale/revoked/approval.
- Consultas e mutações exigem tenant; FKs compostas ligam runs/events/transitions/outbox/DLQ/approvals.
- Transition exige event existente do mesmo run/tenant; `append_event` com `run_id` exige run existente do mesmo tenant; outbox exige evento/run/tenant/payload_ref consistentes e rejeita run terminal; DLQ exige run existente e referência opaca; revisão é obrigatória.
- Colisão de event_id/idempotency com conteúdo divergente é rejeitada; event store é append-only por trigger; SQL é parametrizado.
- WAL é obrigatório: falha ao habilitar WAL aborta a abertura do ledger, sem fallback silencioso; `integrity()` verifica `integrity_check` e `foreign_key_check`.
- SQLite é explicitamente armazenamento local/offline, **não** fronteira de isolamento produtiva.

### F03 — nonce e aprovação duráveis

- Nonce exige `expires_at > now`; nonce expirado, inválido ou reutilizado nega.
- Retenção conservadora de 24h após expiração; não há limpeza prematura por relógio/retrocesso.
- Aprovação e resultado são persistidos em `approvals` com escopo completo (actor/project/task/workflow/risk/policy_epoch/target/approver_role/evidence_refs/max_spend/issued_at); `run_id` é nullable para ações de evento/recovery, e `runs.approval_id` é atualizado no create.
- Migração v3 é transacional e resiliente a approvals legados com `approval_id` duplicado, `approvals_v3` parcial e retomada após rename; schema v4 adiciona `runs.risk`, faz backfill fail-closed a partir do evento (HIGH_ASSURANCE para ausente, não-string, lista/objeto ou risco inválido) e é resumível/idempotente, inclusive para `runs.risk` corrompido.
- Consumo, decisão e mutação ficam na mesma transação; falha de storage/rollback reverte o conjunto, inclusive nonce já consumido.
- HMAC permanece test-only; nenhuma chave/identidade produtiva foi criada.

### F04 — recovery, fencing e retry

- Recovery libera lease expirada, incrementa attempts/revision atomicamente e leva a RETRY_WAIT ou FAILED no cap.
- Run stale, revogada ou com deadline expirado vai direto a FAILED no recovery; nunca retorna a RETRY_WAIT. Reverse de stale/revogação é negado.
- Recovery nunca grava attempts acima do cap 2, mesmo para linha legacy em attempts=2; `retry_decision` usa o mesmo corte de 2 tentativas totais do ledger.
- `BLOCKED` é estado explícito com saídas definidas (QUEUED/CANCELLED/FAILED) e não permite outbox.
- Lease ativa não é tocada; EFFECT_IN_PROGRESS só vira UNKNOWN_EFFECT quando a lease expirou/está ausente. Claim é permitido em RUNNING e EFFECT_IN_PROGRESS, exige deadline futuro e attempts abaixo do cap, permitindo verificação normal do efeito.
- UNKNOWN_EFFECT → VERIFIED/FAILED/BLOCKED exige `reconciliation_ref`.
- Mutações em RUNNING/EFFECT_IN_PROGRESS exigem lease owner/epoch válidos; fencing antigo e owner divergente negam.
- Retry 429/5xx respeita o mesmo cap 2 do ledger; `retry_decision(500,1)` e `retry_decision(429,1)` retornam FAILED.
- Deadline e TTL são validados; correções permanecem no mesmo run; efeito externo nunca é reexecutado cegamente.

### F05 — requisitos originais restaurados

| Requisito original | Implementação |
|---|---|
| 1. Event Contract estrito | `workflow/contracts.py` + `schemas/event-v1.json` |
| 2. Run Contract completo | `RunContract` + `runs` persistido |
| 3. Schemas versionados | `workflow/schemas/*.json` |
| 4. Ledger persistente | SQLite WAL/FULL, eventos/transições/aprovações |
| 5. Migrações versionadas | `workflow/migrations.py`, `schema_migrations`, versão 4 |
| 6. Nonce durável | tabela `nonces`, retenção, atomicidade |
| 7. Máquina de estados com autorização | `WorkflowCommands` + `TRANSITIONS` |
| 8. Compilador dos 62 workflows | `workflow/compiler.py`, 62/62 |
| 9. DAG por execução | `compile_run` + `validate_dag` |
| 10. Source lock/deadline/stale/revogação | RunContract e transições fail-closed |
| 11. CLI verify/compile/dry-run | `python -m workflow verify|compile|dry-run` |
| 12. Contrato C12 | cinco workflows, dispatcher canônico, DISABLED |
| 13. Concorrência/recovery/integridade | testes adversariais + constraints |
| 14. Auditoria independente | pendente do HEAD final |

### F06 — Context Lock e C12

- `workflow verify` valida base tree, ancestralidade do base, `origin/main` obrigatório, drift de fontes e de implementação, fingerprints canônicos no base e no HEAD (exceto arquivos também cobertos pela implementação), 24 canônicos + 17 de implementação, source lock 364 e C12.
- C12 usa allowlist de campos no workflow e nos steps; qualquer campo desconhecido, variação de case ou sinônimo (`Memory_Grants`, `memory_grant`, `skill_grant`, `client_permission`, `entitlements`, `secrets`) é rejeitado, sem mascaramento.
- O invariante de zero grants é verificado recursivamente em todos os 62 workflows e steps; `summary.grants` do compilador é derivado dessa varredura, não literal.
- O run persiste `risk`; comandos STANDARD não transicionam/gerenciam run criado como HIGH_ASSURANCE.
- 62 workflows preservados: 36 INTERNAL_ONLY, 12 POLICY_GATED_EXTERNAL, 14 HUMAN_APPROVAL_REQUIRED; todos DISABLED; zero grants externos.

## 3. Testes executados

| Verificação | Resultado |
|---|---|
| Suíte completa local Windows 11 | **156/156 OK** (120 anteriores preservados + 36 novos: 35 adversariais + 1 regressão de catálogo) |
| `python -m workflow verify` | `WORKFLOW_OK workflows=62 c12=5 events=1 runs=1 nonces=0` |
| `python -m workflow compile` | 62 workflows compilados; summary 36/12/14; 0 grants |
| `python -m workflow dry-run` | DAG determinístico, `execution_allowed=false`, 0 efeitos |
| Source validator | 7/7 grupos PASS; 364 fontes |
| Registry | 105/92/1110; 105 intents; 0 writes |
| Security verify | PASS |
| Security scanner | 493 arquivos, 0 achados |
| `git diff --check` | limpo |

Testes adversariais cobrem: mutação sem grant; grant de outro tenant; revisão obsoleta; command boundary; referências cross-tenant/run; append com run inexistente/de outro tenant; idempotência divergente; nonce expirado/replay/concorrência entre conexões independentes; rollback de nonce após mutação falha; recovery/lease/cap; stale/deadline expirado sem retry; attempts nunca acima do cap; reversão de revogação negada; `approval_id` persistido no run; aprovação de append/recovery; binding de parâmetros de outbox, append run e policy epoch; downgrade de risco negado; run HIGH_ASSURANCE rejeita transição STANDARD; EFFECT_IN_PROGRESS claim/verify; BLOCKED com saída e sem outbox; outbox em run terminal negado; migração v2 com approval_id duplicado, approvals_v3 parcial e retomada de v3; backfill de risco legado HIGH_ASSURANCE, risk lista/objeto e risk corrompido, e v4 resumível; WAL e integridade FK; UNKNOWN_EFFECT sem evidência; DAG circular; workflow desconhecido; C12 dispatcher, variações de privilégio e campos aninhados; zero grants fora C12; retry 429/cap consistente; schemas obrigatórios.

## 4. CI e gates

- CI/CD-02 no code head `3618339b32205557e23c8330e1ead53191398d45`: run **46050653703** — `docs-validation` (ubuntu-24.04, suíte canônica 156 testes, Source Pack, registry, security, workflow verify, compile/dry-run e scanner) e `security-windows` (windows-2025, security/workflow/adversarial, verify/compile/dry-run) **SUCCESS**.
- SonarCloud no HEAD `3618339`: **0 issues abertas**, Quality Gate **passed**, check **success**. As 13 issues de `f503d36` (S5655 CRITICAL, S107, S7519, S7498, S5914 e 8× S5778) permanecem corrigidas sem supressão/NOSONAR.
- Socket Security: Pull Request Alerts e Project Report **PASS**; ECC Tools / Security Evidence **PASS** no commit `3618339`.
- O commit docs-only seguinte registra este read-back e contém o lock final; a auditoria independente do HEAD final permanece pendente.
- O CI executa explicitamente `workflow compile`, `workflow dry-run` e os testes adversariais no Windows.
- Nenhum APPROVED é declarado antes da nova auditoria independente HIGH_ASSURANCE no HEAD final.
- Cobertura Sonar 0.0% continua sendo ausência de relatório/instrumentação, não cobertura; não há alegação de cobertura.

## 5. Acceptance Criteria CD-02

| AC | Status |
|---|---|
| AC01 Context Lock/base tree/364/fingerprints | **PASS local** |
| AC02 Event Contract estrito | **PASS** |
| AC03 Run Contract, ledger durável, migrações, imutabilidade | **PASS** |
| AC04 Máquina de estados e APPROVED→VERIFIED→COMPLETED | **PASS** |
| AC05 Autorização deny-by-default e fronteira de comandos | **PASS** |
| AC06 Aprovação/nonce durável, replay/rollback | **PASS offline** (identidade/custódia produtiva é gate posterior) |
| AC07 Atomicidade run/evento/transição | **PASS** |
| AC08 Concorrência, leases, fencing | **PASS** |
| AC09 Recovery, retry cap, reconciliação | **PASS** |
| AC10 Outbox/DLQ/referências sanitizadas | **PASS** |
| AC11 C12 cinco workflows, dispatcher canônico, sem grants | **PASS** |
| AC12 Retry/limites/deadline | **PASS** |
| AC13 CLI verify/compile/dry-run | **PASS** |
| AC14 CI Linux/Windows, Sonar/Socket/ECC, auditoria | **GATES PASS em 3618339; auditoria independente do HEAD final pendente** |

## 6. Limitações e riscos

- SQLite é storage local; não é isolamento/ledger produtivo.
- Identidade humana real, custódia de chaves de aprovação e provider de assinatura continuam gates de produção fora do CD-02.
- `retry_decision` é contrato puro de política (401/403/429/5xx/cap); não há rota HTTP/effect neste slice offline para integrá-lo.
- `counts()`/`integrity()` permanecem leituras globais de diagnóstico, não caminhos de mutação.
- Windows CI executará security, workflow e adversarial suites; a suíte integral de 156 roda no Linux e localmente no Windows.
- Cobertura não medida; `required_approving_review_count=0` permanece risco de governança.
- Nenhum efeito externo, VPS, Paperclip runtime, segredo, agente, workflow ativo, deploy, merge ou despesa.

## 7. Checkpoint Delta proposto

- Submeter CD-02 à auditoria independente HIGH_ASSURANCE no HEAD final; somente após APPROVED propor checkpoint/merge ao proprietário.
- Não iniciar NLE-WF-WO-002 nem outro Work Order. Sem promoção nesta execução.
