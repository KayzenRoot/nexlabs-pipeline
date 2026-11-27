# NLE-WF-WO-001/CD-02 — HIGH_ASSURANCE Correction Delta evidence

Data: 2026-11-27
Repositório: `KayzenRoot/nexlabs-pipeline`
PR: #10 (draft, branch `work/nle-wf-wo-001`)
Base: `04724af867659e278210489c8ba91fc6344e3fb1`
Base tree: `d0f135f2ba896a5fe22f21610bae78f025c0650e`
HEAD anterior auditado: `82180fa4c9a29fc735ecb492c1e497bc75d0d53a`
Status: **CANDIDATE_PENDING_CD02_INDEPENDENT_AUDIT**

## 1. Escopo e proveniência

A auditoria oficial do ChatGPT em `82180fa` emitiu **CORRECTION REQUIRED** com F01–F06 HIGH/MEDIUM. Esta CD-02 corrige o código no mesmo Work Order, branch e PR #10. Não cria Work Order, não faz merge, não promove checkpoint, não inicia NLE-WF-WO-002/INFRA-WO-003, não acessa VPS/rede/segredos/Paperclip runtime e não gera gasto.

## 2. Correções F01–F06

### F01 — fronteira única de comandos autorizados

- `workflow/commands.py`: `WorkflowCommands` é a única API pública de mutação; Ledger expõe somente leitura e primitivas privadas `_*`.
- Cada comando usa `security.authorization`/`security.approval`; a transação abrange autorização, nonce, mutação, transição e registro de aprovação.
- Decisão vinculada a principal, tenant, project, task, workflow, target/run, ação, payload, risco, policy e epoch; ações desconhecidas, grant ausente/escopo divergente e revisão obsoleta negam.
- `APPROVED → VERIFIED → COMPLETED`; `APPROVED → COMPLETED` não existe. Efeitos externos permanecem negados; o ledger é apenas armazenamento offline.

### F02 — integridade, referências e isolamento

- `runs` carrega tenant/project/task/workflow/version/event/correlation/source-lock/deadline/stale/revoked/approval.
- Consultas e mutações exigem tenant; FKs compostas ligam runs/events/transitions/outbox/DLQ/approvals.
- Transition exige event existente do mesmo run/tenant; outbox exige evento/run/tenant/payload_ref consistentes; DLQ exige run existente; revisão é obrigatória.
- Colisão de event_id/idempotency com conteúdo divergente é rejeitada; event store é append-only por trigger; SQL é parametrizado.
- SQLite é explicitamente armazenamento local/offline, **não** fronteira de isolamento produtiva.

### F03 — nonce e aprovação duráveis

- Nonce exige `expires_at > now`; nonce expirado, inválido ou reutilizado nega.
- Retenção conservadora de 24h após expiração; não há limpeza prematura por relógio/retrocesso.
- Aprovação e resultado são persistidos em `approvals`; nonce, run, tenant e approval_id ficam vinculados.
- Consumo, decisão e mutação ficam na mesma transação; falha de storage/rollback reverte o conjunto.
- HMAC permanece test-only; nenhuma chave/identidade produtiva foi criada.

### F04 — recovery, fencing e retry

- Recovery libera lease expirada, incrementa attempts/revision atomicamente e leva a RETRY_WAIT ou FAILED no cap.
- Lease ativa não é tocada; EFFECT_IN_PROGRESS só vira UNKNOWN_EFFECT quando a lease expirou/está ausente.
- Mutações em RUNNING/EFFECT_IN_PROGRESS exigem lease owner/epoch válidos; fencing antigo e owner divergente negam.
- UNKNOWN_EFFECT → VERIFIED/FAILED exige `reconciliation_ref`; retry 429/5xx respeita o cap 2 em todas as rotas.
- Deadline e TTL são validados; correções permanecem no mesmo run; efeito externo nunca é reexecutado cegamente.

### F05 — requisitos originais restaurados

| Requisito original | Implementação |
|---|---|
| 1. Event Contract estrito | `workflow/contracts.py` + `schemas/event-v1.json` |
| 2. Run Contract completo | `RunContract` + `runs` persistido |
| 3. Schemas versionados | `workflow/schemas/*.json` |
| 4. Ledger persistente | SQLite WAL/FULL, eventos/transições/aprovações |
| 5. Migrações versionadas | `workflow/migrations.py`, `schema_migrations`, versão 2 |
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

- `workflow verify` valida base tree, ancestralidade do base, main atual (quando o ref existe), drift de fontes, 24 fingerprints canônicos + 10 de implementação, source lock 364 e C12.
- C12 exige exatamente GOV-03/QNT-01/02/03/05, dispatcher `NLE-ATHENA-PMO`, e rejeita dispatcher executor/accountable/reviewer, elevação, grants, memória, skills, efeitos e ativação.
- 62 workflows preservados: 36 INTERNAL_ONLY, 12 POLICY_GATED_EXTERNAL, 14 HUMAN_APPROVAL_REQUIRED; todos DISABLED; zero grants externos.

## 3. Testes executados

| Verificação | Resultado |
|---|---|
| Suíte completa local Windows 11 | **137/137 OK** (120 anteriores + 17 adversariais) |
| `python -m workflow verify` | `WORKFLOW_OK workflows=62 c12=5 events=1 runs=1 nonces=0` |
| `python -m workflow compile` | 62 workflows compilados; summary 36/12/14; 0 grants |
| `python -m workflow dry-run` | DAG determinístico, `execution_allowed=false`, 0 efeitos |
| Source validator | 7/7 grupos PASS; 364 fontes |
| Registry | 105/92/1110; 105 intents; 0 writes |
| Security verify | PASS |
| Security scanner | 485 arquivos, 0 achados |
| `git diff --check` | limpo |

Testes adversariais cobrem: mutação sem grant; grant de outro tenant; revisão obsoleta; command boundary; referências cross-tenant/run; idempotência divergente; nonce expirado/replay/concorrência entre conexões independentes; recovery/lease/cap; UNKNOWN_EFFECT sem evidência; migração; DAG circular; workflow desconhecido; C12 dispatcher substitution; retry 429 no cap; schemas.

## 4. CI e gates

- CI/CD-02: run **46027613376** no HEAD `b474ee79c067d53282e9cbe49f8f88c4222af984` — `docs-validation` (ubuntu-24.04, 137 testes) e `security-windows` (windows-2025, security+workflow) **SUCCESS**.
- SonarCloud: **0 issues abertas**, quality gate **OK**, check pass.
- Socket Security: Pull Request Alerts/Project Report **PASS**; ECC Security Evidence **PASS**.
- O commit final de evidência/lock é docs-only após este HEAD de código; o HEAD final verificável é registrado no PR #10.
- Nenhum APPROVED é declarado antes da nova auditoria independente HIGH_ASSURANCE.
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
| AC14 CI Linux/Windows, Sonar/Socket/ECC, auditoria | **PASS gates; auditoria independente pendente** |

## 6. Limitações e riscos

- SQLite é storage local; não é isolamento/ledger produtivo.
- Identidade humana real, custódia de chaves de aprovação e provider de assinatura continuam gates de produção fora do CD-02.
- Windows CI executará security + workflow suites; a suíte integral de 136 roda no Linux e localmente no Windows.
- Cobertura não medida; `required_approving_review_count=0` permanece risco de governança.
- Nenhum efeito externo, VPS, Paperclip runtime, segredo, agente, workflow ativo, deploy, merge ou despesa.

## 7. Checkpoint Delta proposto

- Submeter CD-02 à auditoria independente HIGH_ASSURANCE no HEAD final; somente após APPROVED propor checkpoint/merge ao proprietário.
- Não iniciar NLE-WF-WO-002 nem outro Work Order. Sem promoção nesta execução.
