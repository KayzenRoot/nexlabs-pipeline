# Evidence Bundle | NLE-BOOTSTRAP-001/CD-03

Status: **ROUND1_CORRECTIONS_APPLIED_PENDING_REAUDIT**. Auditoria Round 1: CORRECTION REQUIRED (H1–H3/M1–M2); correções aplicadas; Round 2 pendente. Nenhum APPROVED declarado.

## 1. Source Check

| Item | Resultado |
|---|---|
| Repositório | `KayzenRoot/nexlabs-pipeline`, ID `1472951510`, público, não arquivado |
| Base | `48d3e422313f869992d09b99f0b7e09acd4e1caa` |
| Branch/PR | `chore/nle-bootstrap-001`, PR #1 draft |
| HEAD inicial CD-03 | `70418070aa80b2b35093be46e87fb246eacfeb6a` |
| HEAD auditado | `668a77eb5683254018476cdeb02dcfdfcbbc6ca6` |
| HEAD final | registrado no comentário da PR #1 após o push, sem hash autorreferente |
| Actions | habilitado; `allowed_actions=all`; permissões padrão `read` |
| Runners self-hosted | 0 |
| Runner CI | `ubuntu-24.04` padrão GitHub-hosted |
| Checkout | `actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09` (v5.1.0), SHA integral verificado |
| Source Pack | 364/364 + 6 ZIPs; source-lock SHA-256 `a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e` |
| ZIP | 1.557.156 bytes, SHA-256 `1c012736772aba8a96bc27f796194d4a77f1f88a7ff66ee37c2512f2d6129844` |
| Proveniência | `docs/Provenance.md` separa pacote original e estado Git remoto |

## 2. Workflow versionado

`.github/workflows/docs-validation.yml`:

- `on: pull_request` para `main`.
- `permissions: contents: read` no workflow e no job.
- `runs-on: ubuntu-24.04`, `timeout-minutes: 15`.
- Concorrência por PR com cancelamento.
- Checkout oficial pinado por SHA, `persist-credentials: false`, `fetch-depth: 1`.
- `python3 scripts/validate_sources.py`.
- `python3 -m unittest discover -s tests -v`.
- Sem secrets, cache, artefatos, deploy, `pull_request_target` ou runner maior.

## 3. CI real

| Item | Valor |
|---|---|
| Run | `45826789668` — https://github.com/KayzenRoot/nexlabs-pipeline/actions/runs/45826789668 |
| Nome | `docs-validation` |
| Evento | `pull_request` |
| HEAD | `668a77eb5683254018476cdeb02dcfdfcbbc6ca6` |
| Conclusão | **success** |
| Job | `docs-validation`, success |
| Runner | `GitHub Actions 1000114778`, grupo `GitHub Actions`, labels `["ubuntu-24.04"]` |
| Início/fim | 13:11:54Z / 13:12:05Z (aprox. 11s de job) |
| Python | 3.12.3 |
| Validador | 7 grupos PASS |
| Testes | 7/7 OK em 0.578s |

Logs (excertos):

```text
Python 3.12.3
PASS: 6 ZIPs and 364 locked source files, extracted bytes preserved
PASS: all embedded cross-plan source locks match
PASS: 105 agents, 316 individual scenarios, 92 packages, 1110 assignments, 1071 contextual competencies, hierarchy and disabled baseline
PASS: 5 dispatch-only discrepancies preserved; C12 requires correction before runtime
PASS: 62 workflows, 638 matrix rows, 1110 trace rows, reviewer segregation and gates
PASS: INT/INFRA/CC bindings and 35 screens, 48/32/59 planned scenarios, resource and cost caps
PASS: 40 domain WOs, no missing/duplicate IDs, sequential gate
Ran 7 tests in 0.578s
OK
```

Execução anterior `45826493317` (checkout v4.4.0) também passou, mas foi superseded por `668a77e` para remover o aviso de Node 20. O run final é `45826789668`.

## 4. Custo e runner

- Repositório **público** + runner **padrão** `ubuntu-24.04` + checkout oficial gratuito.
- Nenhum runner maior, self-hosted, serviço pago, cache, artefato, secret ou deploy.
- Política pública do GitHub: runners padrão são gratuitos em repositórios públicos; larger runners são cobrados e **não** foram usados.
- Custo adicional: **US$0**. O read-back de billing por API continua indisponível por escopo de token; não há recurso faturável no workflow.

## 5. Check obrigatório e governança

- Após o sucesso do run `45826789668` e read-back, `docs-validation` foi configurado como required status check da `main`.
- Read-back: `strict=true`, `contexts=["docs-validation"]`, `checks=[{context:"docs-validation", app_id:15368}]`.
- Proteção da `main`: PR obrigatório, `required_approving_review_count=0`, `dismiss_stale_reviews=true`, `enforce_admins=true`, `required_linear_history=true`, `allow_force_pushes=false`, `allow_deletions=false`, `required_conversation_resolution=true`.
- Ruleset `main-bootstrap-protection` (ID `28163842`): non-fast-forward e deletion, ativo, `bypass_actors=[]`, `current_user_can_bypass=never`.
- Merge: squash-only; merge commit/rebase desabilitados; delete branch on merge desabilitado; auto-merge desabilitado.
- PR #1 permanece OPEN/draft, sem merge.

## 6. Documentação e reconciliação

- `docs/Provenance.md` separa proveniência do pacote original (ZIP SHA-256, source-lock, 364/364) do estado Git remoto (repo, base, branch, PR, HEAD, CI, governança).
- `work-orders/NLE-BOOTSTRAP-001.md` reconcilia o WO com **NLE-ADR-BOOT-007**: a decisão ratificada vigente autoriza o repositório público temporário para material revisado e não sensível; produção permanece privada. Textos private-only anteriores são históricos e preservados.
- `locks/context-lock.json` registra o HEAD auditado `668a77e`, o source-lock, o run de CI e o check obrigatório; o HEAD final fica neste Evidence Bundle/PR.
- README, Checkpoint, Governance, DoD e Consistency-Audit foram atualizados sem apagar decisões ou histórico.

## 7. Auditoria Round 1 e correções

O auditor independente (agente read-only) auditou `668a77e` e emitiu **CORRECTION REQUIRED**:

- H1: Evidence Bundle em rascunho, pin v4.4.0 incorreto, sem run/logs/check.
- H2: Context Lock/docs com `head_audited=null`, `runs=0`, pendências.
- H3: working tree alterada sem commit durante a auditoria.
- M1: corpo da PR stale.
- M2: `source-lock` com status histórico não explicitado.

Correções aplicadas neste commit: bundle com pin v5.1.0, run `45826789668`, logs, 7 PASS + 7/7 e check; lock com `head_audited=668a77e`, CI e check; docs de estado atualizados; working tree limpa; Provenance marca o status histórico do source-lock; Governance/Ledger marcam o texto private-only como histórico. Relatório completo: `evidence/NLE-BOOTSTRAP-001-CD03-AUDIT-ROUND1.md`.

## 8. AC01–AC09

| AC | Status | Evidência |
|---|---|---|
| AC01 CI no HEAD auditado | **PASS** | run `45826789668` success em `668a77e` |
| AC02 US$0 e runner padrão | **PASS** | público + `ubuntu-24.04` + nenhum recurso pago; política GitHub; sem larger/self-hosted |
| AC03 Check obrigatório | **PASS** | `docs-validation`, app_id `15368`, `strict=true`, read-back |
| AC04 Context Lock/Source Lock | **PASS** | source-lock 364/364; Context Lock com HEAD auditado/CI/check |
| AC05 ADR-BOOT-007 e WO | **PASS documental** | `docs/Provenance.md`, WO CD-03 e Governance reconciliados |
| AC06 Segurança/integridade | **PASS (corrigido; Round 2 pending)** | workflow least privilege; 402 arquivos sem segredos/PII; integridade 364/364 |
| AC07 C12 preservado | **PASS** | C12 permanece gate de runtime; 5 dispatch-only preservados |
| AC08 Evidence Bundle | **PASS (corrigido; Round 2 pending)** | este bundle + run/logs/check; HEAD final no comentário |
| AC09 Auditoria independente | **PENDING ROUND 2** | Round 1 CORRECTION REQUIRED; reauditoria do commit corretivo pendente |

## 9. Veredito

**PENDING ROUND 2** — não declarar APPROVED antes da reauditoria do commit corretivo e da CI no novo HEAD. Nenhum merge, deploy, gasto, promoção de checkpoint ou início de NLE-INFRA-WO-001.
