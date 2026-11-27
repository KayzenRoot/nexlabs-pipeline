# NLE-INFRA-WO-002/CD-01.2 — Correction Delta de governança e proveniência

Data: 2026-11-27
Repositório: `KayzenRoot/nexlabs-pipeline`
PR: #7 (draft, branch `work/nle-infra-wo-002-cd01`)
Base SHA: `eebbd7325ab45fca8e176bd713245189ed148bdd`
Base tree SHA: `8d8cbf1a5c4ce752c4df8787f1c79d4d15f04e33` (confirmado com `git rev-parse <BASE>^{tree}`)
HEAD anterior: `af8ead31d78dd30b1daf8fce22366b0d06cb59d0`
Status: **CORRECTION DELTA APPLIED — PENDING INDEPENDENT AUDIT**
Escopo: somente Context Lock, fingerprints, decisões documentais, proveniência de auditoria e evidência. Nenhuma alteração no runtime de segurança aprovado.

## 1. Resumo executivo

Foram corrigidas as divergências F01–F05 identificadas na auditoria documental:

- **F01:** `base_tree_sha` do Context Lock apontava para o SHA do commit base, não para a árvore Git. Corrigido para `8d8cbf1a5c4ce752c4df8787f1c79d4d15f04e33`.
- **F02:** a auditoria independente foi registrada em HEAD anterior ao HEAD documental final. O histórico foi preservado e esta revisão CD-01.2 está marcada como **pendente de auditoria independente externa**; nenhum APPROVED foi inventado para o HEAD final.
- **F03:** `docs/decisions-index.json` marcava `INFRA-ADR-001..010` como `RATIFIED_DIRECTION`, enquanto o Source Pack declara **todas PROPOSED**. O índice foi corrigido; a ratificação da direção geral `NLE-INFRA-PLAN-001` foi preservada.
- **F04:** diferença de rigor entre schemas JSON e validadores Python foi classificada como não bloqueante neste incremento e permanece fora de escopo (sem alteração).
- **F05:** proteção da `main` foi lida integralmente; nenhum ruleset/permissão foi alterado.

Nenhum código de segurança, teste, workflow, fonte, deploy ou runtime Paperclip foi alterado neste incremento. Nenhum merge, promoção, VPS, rede, credencial, agente, workflow, modelo ou gasto.

## 2. Source Check

- `git fetch` completo; PR #7 confirmada OPEN, draft, mergeable.
- Base real: `eebbd7325ab45fca8e176bd713245189ed148bdd`.
- Árvore real da base: `8d8cbf1a5c4ce752c4df8787f1c79d4d15f04e33`.
- HEAD anterior: `af8ead31d78dd30b1daf8fce22366b0d06cb59d0`; branch e remoto coincidem.
- Nenhuma divergência externa inesperada; o preflight não exigiu recompilar a base antes da correção.

## 3. Context Lock e fingerprints

O lock agora separa explicitamente:

- **Canonical/base:** 27 arquivos críticos, com blobs/SHA-256 extraídos da árvore `8d8cbf1…`, incluindo `docs/decisions-index.json` e `.github/workflows/docs-validation.yml` na versão da base.
- **Implementation/HEAD:** 22 arquivos da implementação CD-01 e desta correção documental, incluindo `security/…`, testes, Work Order, evidências e o `docs/decisions-index.json` corrigido.

Verificação conhecida preservada:

- workflow na base: `137a06448282fb224420cf5037e0016def5e2cc8`;
- workflow na implementação: `9af099ea1d60810b2d8b84af9654e985128e7f4a`.

Os dois conjuntos não foram misturados. O lock contém mapas Git blob e SHA-256 separados, e a verificação local exige zero divergências. O fingerprint canônico de `docs/decisions-index.json` registra o conteúdo histórico da base; o fingerprint de implementação registra o índice corrigido. A validação final dos 27+22 fingerprints é executada após a gravação deste arquivo e registrada no commit.

## 4. Decisões — INFRA-ADR-001..010

Inspeção individual no Source Pack:

- `sources/NexLabs_Infrastructure_Plan/README.md` §10: “Todas PROPOSED; preservar a ratificação do INT e não inventar ADR Git aprovada.”
- `docs/Decisions-Ledger.md`: `NLE-INFRA-PLAN-001` permanece `RATIFIED_DIRECTION` (direção geral), e não ratifica individualmente os INFRA-ADRs.
- `docs/decisions-index.json`: os dez `INFRA-ADR-001..010` estavam `RATIFIED_DIRECTION`; corrigidos para `PROPOSED`, com `implementation_approved: false` preservado.

Não houve alteração do Source Pack, do Ledger de direção geral, de ADRs históricas ou de decisões aprovadas. Nenhuma nova ADR foi introduzida. Validação: as 10 entradas `INFRA-ADR-001..010` estão `PROPOSED`; `NLE-INFRA-PLAN-001` permanece `RATIFIED_DIRECTION`; `implementation_approved` permanece `false`.

## 5. Proveniência de auditoria

Registro transparente, sem promoção retroativa:

- **Auditoria histórica de código/segurança:** HEAD `578c273f937423758d2d37abb96c70e342357978`, verdict APPROVED, baseada em revisão de dossiê, sem reexecução de ferramentas pelo auditor. Permanece como evidência histórica do code/security scope.
- **Revisão de dossiê no HEAD documental `af8ead3`:** APPROVED, também sem reexecução de ferramentas; documentada como revisão de dossiê, não como auditoria independente tool-level do HEAD final.
- **CD-01.2 (este commit):** **PENDING_EXTERNAL_INDEPENDENT_AUDIT**. Não há APPROVED para o HEAD documental final.
- O Context Lock não tenta conter o SHA do próprio commit; o HEAD final verificável é registrado no Evidence Bundle externo/PR.

## 6. Proteção da branch (read-back)

`GET /repos/KayzenRoot/nexlabs-pipeline/branches/main/protection` e rulesets:

- required status check: `docs-validation`, `app_id=15368`, `strict=true`;
- enforce admins: `true`;
- force pushes: `false`;
- deletions: `false`;
- linear history: `true`;
- required conversation resolution: `true`;
- required approving reviews: `0` (risco residual de governança, não alterado);
- ruleset `main-bootstrap-protection` ID `28163842`, enforcement `active`, sem bypass.

Nenhum ruleset, permissão ou configuração GitHub foi modificado.

## 7. Arquivos alterados neste incremento

- `docs/decisions-index.json` — 10 status de INFRA-ADR corrigidos para PROPOSED.
- `locks/NLE-INFRA-WO-002-context-lock.json` — base tree, separação canonical/implementation, proveniência, CI/auditoria e fingerprints.
- `evidence/NLE-INFRA-WO-002-CD01.2-EXECUTION.md` — este Evidence Bundle.

Nenhum arquivo em `security/`, `tests/`, `.github/workflows/`, `sources/`, `deploy/`, `scripts/windows/` ou runtime Paperclip foi alterado.

## 8. Testes e validações

Executados no worktree, Windows 11:

| Verificação | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` | **98/98 OK** |
| `python -m security verify` | `SECURITY_CONTRACTS_OK default_deny=true network=offline secrets=opaque` |
| `python -m registry verify` | 105 agentes / 92 pacotes / 1.110 assignments; 105 intents; 0 runtime writes |
| `python scripts/validate_sources.py` | 7/7 grupos PASS; 364 fontes |
| `python scripts/security/scan_repository.py` | 473 arquivos; 0 achados |
| `python -m json.tool docs/decisions-index.json` | JSON válido |
| Verificação de fingerprints base/HEAD | 27 canônicos + 22 implementação; zero divergências |
| `git diff --check` | limpo |

CI do HEAD anterior `af8ead3`: run `45908617377` — `docs-validation` (ubuntu-24.04) e `security-windows` (windows-2025) SUCCESS; SonarCloud 0 issues/gate OK; ECC Security Evidence PASS; Socket PASS. O run do HEAD documental CD-01.2 é verificado externamente após o push e registrado na PR #7.

## 9. SonarCloud, Socket, ECC e cobertura

- SonarCloud no HEAD de código `af8ead3`: **0 issues abertas**, quality gate OK. A alteração CD-01.2 é documental; a reanálise do novo HEAD é verificada após o push.
- Socket Security: PASS no HEAD anterior; novo HEAD verificado após o push.
- ECC Security Evidence: PASS no HEAD anterior; novo HEAD verificado após o push.
- Cobertura nova de código: 0.0% por ausência de instrumentação/relatório/upload; `new_lines_to_cover=0`; o quality gate não possui condição de cobertura. AC08 “100% targeted tests” permanece interpretado como 98/98 pass rate, não como cobertura. Não há alegação de cobertura.

## 10. Limitações, riscos e pendências

1. **Auditoria externa do HEAD documental CD-01.2 ainda não existe.** O veredito proposto é `CORRECTION DELTA APPLIED — PENDING INDEPENDENT AUDIT`, não APPROVED.
2. **F04** — diferença de rigor entre schemas e validadores Python é não bloqueante e fora de escopo; não foi alterada.
3. **F05** — `required_approving_review_count=0` permanece risco de governança; nenhum ruleset foi alterado.
4. Cobertura de novo código continua sem relatório; não confundir com testes.
5. O backup/restore não é objeto deste incremento; nenhum runtime foi tocado.
6. A aprovação de código/segurança em `578c273` é histórica; não se estende automaticamente ao HEAD documental final.

## 11. Checkpoint Delta proposto (não promovido)

- Corrigir o checkpoint documental somente após auditoria independente externa do HEAD final.
- Não promover checkpoint, não fazer merge, não iniciar NLE-WF-WO-001, não acessar VPS, não configurar rede, não criar/rotacionar credenciais, não importar skills, não ativar agentes/workflows, não chamar modelos e não gerar despesa.
- O próximo passo é a auditoria independente de `docs/decisions-index.json`, Context Lock, fingerprints, proveniência e Evidence Bundle no HEAD final.

## 12. Veredito proposto

**CORRECTION DELTA APPLIED — PENDING INDEPENDENT AUDIT.**

As divergências F01–F03 e F05 foram corrigidas; F04 foi registrada como fora de escopo; F02 foi tratada sem falsificar auditoria no HEAD final. A implementação de segurança aprovada não foi modificada. Aguarda-se auditoria independente externa do HEAD documental.
