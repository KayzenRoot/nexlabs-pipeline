# Evidence Bundle | NLE-BOOTSTRAP-001/CD-02

Data: 2026-11-26
Executor: Principal Engineer (ZCode/Codex CLI, Windows)
Repositório: `KayzenRoot/nexlabs-pipeline` (ID 1472951510)
Base: `48d3e422313f869992d09b99f0b7e09acd4e1caa`
Branch: `chore/nle-bootstrap-001`
PR: #1 (draft) — https://github.com/KayzenRoot/nexlabs-pipeline/pull/1
Head no início desta execução: `9a0d4009fb491a545e917cc1dc1b95d9f2b354f7`
Head final: registrado no comentário de evidência da PR após o push normal; este arquivo não contém hash autorreferente.

## 1. Resumo

O Source Pack completo foi recebido, verificado e reconciliado na branch existente. Os 364 arquivos originais e os seis ZIPs conferem com `locks/source-lock.json`; os 325 arquivos já versionados foram comparados byte a byte com o lock e preservados; os 39 ausentes foram adicionados. O validador canônico passou nos sete grupos e os sete testes passaram. O Context Lock real foi gerado. A governança da `main` foi configurada e lida de volta. O CI permanece **NOT_RUN** porque plano/billing/franquia não foram comprovados com o token disponível; o gate de CI/checks está bloqueado, sem workflow ou runner ativado.

Não há APPROVED independente. Não houve merge, deploy, gasto, ativação de agentes/skills/rotinas ou operação financeira.

## 2. Source Check

| Item | Resultado |
|---|---|
| ZIP de entrega | `NLE-BOOTSTRAP-001_NexLabs_Pipeline.zip`, 1.557.156 bytes |
| SHA-256 do ZIP | `1c012736772aba8a96bc27f796194d4a77f1f88a7ff66ee37c2512f2d6129844` |
| Integridade ZIP | 394 entradas, 4.264.032 bytes extraídos, `testzip()` OK, 0 caminhos inseguros, 0 symlinks |
| Cópias do ZIP | workspace e Downloads com o mesmo SHA-256 |
| `locks/source-lock.json` | SHA-256 `a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e` |
| Arquivos originais | 364/364 hashes SHA-256 conferem; 0 ausentes; 0 divergentes; 0 extras |
| ZIPs originais | 6/6, CRC e bytes extraídos conferem |
| Subconjunto já versionado | 325 arquivos; todos os blobs Git conferem com o lock; 0 divergências; 39 adicionados |
| Árvore Git do subconjunto | `3856ba9b4995443510166cefa5f2550394465be5` (325 arquivos) |
| Contagens | 105 agentes, 92 pacotes, 1.110 atribuições, 1.071 competências contextuais, 62 workflows, 35 superfícies, 316 cenários |
| Baseline | `PROPOSED`, `qualified: 0`, `implemented: 0`, agentes `PLANNED_NOT_QUALIFIED`, efeitos externos `DENY` |
| C12 | Cinco divergências dispatch-only preservadas; correção exigida antes de runtime |

## 3. Correção aplicada

O validador canônico comparava caminhos do working tree Windows com `\` contra chaves POSIX `/` do `source-lock.json`, produzindo `source inventory drift` mesmo com os bytes corretos. Correção mínima de portabilidade, sem alterar a semântica:

- Original: `scripts/validate_sources.py` SHA-256 `02dbc5244011e0284483d7f026ab0f20d68d7e19e31d2d7914a3d804094b0ac6`
- Corrigido: SHA-256 `61fe8bf6e48c7f71d158e7122be1cd7a411ddd2c90b4978ef13739ea16596272`
- Diff: `str(p.relative_to(root))` → `p.relative_to(root).as_posix()` na montagem do inventário de `sources/`.
- Nenhum arquivo em `sources/` foi alterado. Os ZIPs e os 364 originais permanecem byte a byte.

## 4. Testes e evidências reais

Comandos executados na raiz do pacote e na raiz da branch:

| Comando | Resultado |
|---|---|
| `python scripts/validate_sources.py` | 7 grupos PASS; exit 0 |
| `python -m unittest discover -s tests -v` | 7/7 testes OK; exit 0 |
| `git diff --cached --check` (fontes novas) | 0 achados; os 6.863 achados históricos do commit de importação inicial permanecem em `sources/` imutáveis e não foram corrigidos por preservação byte a byte |
| `git diff --cached --check` (`:(exclude)sources`) | exit 0 após normalizar CRLF do Context Lock; docs/scripts/tests limpos |
| Varredura de segredos/PII | 0 chaves privadas, tokens, credenciais em URL, e-mails, IPs públicos, CPF ou CNPJ nos arquivos versionados |
| `git status` | worktree limpo antes do commit; nenhum push/force-push |
| CI remoto | **NOT_RUN**; 0 workflows/runs; nenhum runner ativado |

Saída do validador:

```
PASS: 6 ZIPs and 364 locked source files, extracted bytes preserved
PASS: all embedded cross-plan source locks match
PASS: 105 agents, 316 individual scenarios, 92 packages, 1110 assignments, 1071 contextual competencies, hierarchy and disabled baseline
PASS: 5 dispatch-only discrepancies preserved; C12 requires correction before runtime
PASS: 62 workflows, 638 matrix rows, 1110 trace rows, reviewer segregation and gates
PASS: INT/INFRA/CC bindings and 35 screens, 48/32/59 planned scenarios, resource and cost caps
PASS: 40 domain WOs, no missing/duplicate IDs, sequential gate
```

Saída dos testes:

```
test_added_source ... ok
test_bypassed_predecessor ... ok
test_duplicate_work_order ... ok
test_missing_source ... ok
test_tampered_catalog ... ok
test_unapproved_activation ... ok
test_valid_snapshot ... ok
----------------------------------------------------------------------
Ran 7 tests ... OK
```

## 5. AC01–AC09

| AC | Status | Evidência |
|---|---|---|
| AC01 target/access/base/visibility | **PASS** | Repo ID `1472951510`, base `48d3e42…`, branch/PR corretos; exceção pública NLE-ADR-BOOT-007; owner admin/push |
| AC02 364 originais + 6 ZIPs | **PASS** | 364/364 hashes; 6/6 ZIPs; 0 divergências; 39 adicionados |
| AC03 cross-links/gates/default disabled | **PASS estrutural** | Validador confirma 105/92/1110/1071/62/35, hierarquia, bindings, gates, 5 dispatch-only e baseline desabilitado; C12 permanece gate de runtime |
| AC04 docs canônicos + 40 WOs | **PASS** | Documentos completos do pacote reconciliados; `docs/backlog.json` com 40 IDs; nenhuma duplicação |
| AC05 ratificações/ADRs/conflitos | **PASS documental** | NLE-INT/INFRA/CC, Obsidian, NLE-ADR-BOOT-006/007 preservados; propostas não convertidas em aprovação; histórico CD-01/CD-02 mantido |
| AC06 Context Lock/CI grátis/testes | **PARTIAL/BLOCKED_CI** | Context Lock real e 7/7 + 7/7 PASS; CI gratuito NOT_QUALIFIED por billing/plano não comprovados |
| AC07 governança/squash/custo | **PARTIAL** | `main` com PR obrigatório, histórico linear, squash-only, sem force/delete, sem bypass, conversas resolvidas; checks obrigatórios pendentes de CI; US$0 sem gasto |
| AC08 draft PR + Evidence Bundle | **PASS** | PR #1 draft existente; este Evidence Bundle e o Context Lock serão commitados na mesma branch; head final no comentário da PR |
| AC09 APPROVED independente/promoção/merge | **NOT_STARTED** | Auditoria externa pendente; sem promoção, merge ou autoaprovação |

## 6. Governança e custo

Read-back após configuração:

- Repositório: `allow_squash_merge=true`, `allow_merge_commit=false`, `allow_rebase_merge=false`, `delete_branch_on_merge=false`, `allow_auto_merge=false`.
- Ruleset `main-bootstrap-protection` (ID `28163842`): `non_fast_forward` e `deletion`, `enforcement=active`, `bypass_actors=[]`, `current_user_can_bypass=never`.
- Proteção clássica da `main`: PR obrigatório, `required_approving_review_count=0`, `dismiss_stale_reviews=true`, `enforce_admins=true`, `required_linear_history=true`, `allow_force_pushes=false`, `allow_deletions=false`, `required_conversation_resolution=true`.
- Actions: `enabled=true`, `allowed_actions=all`, `sha_pinning_required=false`, permissões padrão do workflow `read`, aprovação de PR reviews `false`.
- Checks obrigatórios: **NÃO CONFIGURADOS**, pois não há CI comprovado. Não foi criado um check fictício.
- Billing/plano/franquia: API de billing retornou 404 por escopo `user` ausente; plano REST/GraphQL indisponível. **Não** houve refresh de login/token. CI **NOT_RUN**. Custo adicional: **US$0**; nenhuma assinatura, runner pago, deploy ou operação financeira.

## 7. Segurança

- Varredura determinística dos arquivos versionados: 0 chaves privadas, tokens GitHub/AWS/Slack/OpenAI/Google, credenciais em URL, e-mails, IPs públicos, CPF ou CNPJ.
- Nenhum segredo, dado de cliente ou informação operacional sensível foi adicionado ao repositório público.
- `sources/` preservado byte a byte; builders históricos não executados; nenhum `SKILL.md` executável foi criado.
- Exceção pública NLE-ADR-BOOT-007 limitada a planejamento/desenvolvimento revisado e não sensível; produção permanece privada.
- Nenhum force-push, bypass, rewrite, merge ou autoaprovação.

## 8. Riscos residuais

- **CI/checks:** billing/plano não comprovados; o gate permanece bloqueado até prova de US$0 ou autorização específica do proprietário.
- **Auditoria independente:** pendente; nenhum APPROVED é declarado.
- **C12:** dispatch-only do NLE-ATHENA-PMO continua exigindo contrato/teste negativo em WF-WO-001.
- **Governança:** `required_approving_review_count=0` não impõe revisão humana pelo GitHub; a independência é um gate de processo/auditoria, não autoaprovação.
- **Visibilidade:** repositório público durante o bootstrap; conversão futura para privado não apaga cópias públicas anteriores.

## 9. Checkpoint Delta proposto

Manter **`SOURCE_PACK_COMPLETE_PENDING_INDEPENDENT_AUDIT`**. Source Pack, Context Lock, validadores e testes completos. AC06-CI e AC07-checks bloqueados por billing não comprovado. AC09 não iniciado. Nenhuma promoção, merge ou início de NLE-INFRA-WO-001.

## 10. Veredito

**BLOCKED** — exclusivamente no gate CI/billing. O Source Pack, o Context Lock, a validação canônica, os 7 testes, a reconciliação documental e a governança de merge estão completos e prontos para auditoria independente. Não há APPROVED, merge, deploy ou gasto.
