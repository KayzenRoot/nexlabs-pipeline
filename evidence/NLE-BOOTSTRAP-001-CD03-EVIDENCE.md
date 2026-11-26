# Evidence Bundle (draft) | NLE-BOOTSTRAP-001/CD-03

Status: **CI_FREE_QUALIFICATION_IN_PROGRESS**. Este arquivo será completado com o run ID, logs, check obrigatório e auditoria antes do veredito final.

## 1. Source Check

| Item | Resultado |
|---|---|
| Repositório | `KayzenRoot/nexlabs-pipeline`, ID `1472951510`, público, não arquivado |
| Base | `48d3e422313f869992d09b99f0b7e09acd4e1caa` |
| Branch/PR | `chore/nle-bootstrap-001`, PR #1 draft |
| HEAD inicial | `70418070aa80b2b35093be46e87fb246eacfeb6a` |
| Actions | habilitado; `allowed_actions=all`; permissões padrão `read` |
| Runners self-hosted | 0 |
| Runner CI | `ubuntu-24.04` padrão GitHub-hosted |
| Checkout | `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (v4.4.0), SHA integral verificado |
| Custo | público + runner padrão + nenhum recurso pago/cache/artefato/secret; US$0 adicional |
| Source Pack | 364/364 + 6 ZIPs; source-lock SHA-256 `a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e` |
| ZIP | 1.557.156 bytes, SHA-256 `1c012736772aba8a96bc27f796194d4a77f1f88a7ff66ee37c2512f2d6129844` |
| Proveniência | `docs/Provenance.md` separa pacote original e estado Git remoto |

## 2. Workflow

`.github/workflows/docs-validation.yml`:

- `on: pull_request` para `main`.
- `permissions: contents: read` no workflow e no job.
- `runs-on: ubuntu-24.04`, `timeout-minutes: 15`.
- Concorrência por PR com cancelamento.
- Checkout oficial pinado por SHA, `persist-credentials: false`, `fetch-depth: 1`.
- `python3 scripts/validate_sources.py`.
- `python3 -m unittest discover -s tests -v`.
- Sem secrets, cache, artefatos, deploy, `pull_request_target` ou runner maior.

## 3. CI

PENDENTE — primeira execução será disparada pelo push do commit que contém este draft. O run ID, o HEAD exato, os logs e a conclusão serão registrados aqui e no comentário da PR antes do veredito.

## 4. Check obrigatório

PENDENTE — será configurado na proteção da `main` somente após a primeira execução bem-sucedida e read-back do contexto exato do check.

## 5. AC01–AC09

| AC | Status | Evidência |
|---|---|---|
| AC01 CI no HEAD auditado | PENDING | primeira execução pendente |
| AC02 US$0 e runner padrão | PENDING/QUALIFIED_BY_POLICY | público + `ubuntu-24.04` + nenhum recurso pago; run a comprovar |
| AC03 Check obrigatório | PENDING | configuração após sucesso e read-back |
| AC04 Context Lock/Source Lock | PARTIAL | source-lock 364/364; Context Lock CD-03 gravado; HEAD auditado pendente |
| AC05 ADR-BOOT-007 e WO | PASS documental | `docs/Provenance.md`, WO CD-03 e Governance reconciliados |
| AC06 Segurança/integridade | PENDING | revisão independente pendente |
| AC07 C12 preservado | PASS | C12 permanece gate de runtime |
| AC08 Evidence Bundle | DRAFT | run/logs/check/audit pendentes |
| AC09 Auditoria independente | PENDING | auditor separado será executado antes do veredito |

## 6. Veredito

**PENDENTE** — não declarar APPROVED antes da CI, read-back do check e auditoria independente.
