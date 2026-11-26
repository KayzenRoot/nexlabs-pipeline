# NLE-BOOTSTRAP-001 | Source Pack & Governance
## OBJECTIVE
Integrate the planning foundation in target private repo with no implementation or new spend; qualify GitHub governance, CI and source evidence.
## CONTEXT
Owner ratified INT, INFRA, CC and Obsidian; preserve all catalogs. Historical target returned 404. Owner redirected to KayzenRoot/nexlabs-pipeline; admin/push verified, public visibility, no main branch found. BLOCKED_PUBLIC_REPO until private read-back. Local snapshot only. Independent audit required; current bootstrap candidate not merged.
## SCOPE
Resolve target access/identity and existing repo status; read-only inventory and conflict check; use the existing KayzenRoot/nexlabs-pipeline only; no new repo; verify private visibility, minimal initial base if necessary and allowed; place canonical source pack in branch, deterministic validators, CI if proven free, configure authorized GitHub safeguards, open/update draft PR. No domain code.
## OUT OF SCOPE
Install Paperclip, agents, skills, WSL, Docker, router, VPS changes, real customer data, new paid plans, live ads/trades/mainnet/deploy, public exposure, self-approval, destructive Git operations. Preserve existing repo/projects.
## FILES/SOURCES TO READ
README hierarchy; checkpoint, decisions, scope, DoD, architecture, requirements, consistency audit, governance, security, backlog; all locked sources; validators/tests; inspect existing repo before copy. Official GitHub settings/billing and capability docs if needed.
## REQUIREMENTS / ARCHITECTURE RULES
REQ-01/02/04/07/12/15 as foundation only. Preserve exact files and IDs; namespace fixed, privacy, default deny, Git canon, Paperclip operational authority, no third-party runtime. No undocumented API assumption. C02 plugin vs sidecar remains qualified decision; no ADR override.
## CONSTRAINTS
US$0 incremental verified before enabling CI; protect secrets; no force-push, bypass, rewrite, merge before independent approval. If repo already exists, preserve files/decisions and reconcile conflicts in same WO. If private visibility, access or plan gates cannot be verified, BLOCKED. No identity switch or public repo. If branch base absent, document minimal initial commit needed to open PR; no bootstrap direct-to-main. If authorization absent, stop.
## ACCEPTANCE CRITERIA
AC01 target namespace/private/access/base evidence; AC02 6 ZIPs intact and all fingerprints, 105/92/1110/62/35, 1071 contextual records, 316 original agent tests; AC03 cross-links/gates/default disabled/no grants verified; AC04 complete Source Pack and 40 prior WOs exactly once; AC05 ratifications, conflict resolutions/pending ADRs accurately preserved; AC06 Context Lock real SHA and fingerprints, CI free + read-back, local tests; AC07 GitHub protections and squash policy verified, no spend, secret hygiene; AC08 draft PR + Evidence Bundle and proposed checkpoint delta, independent audit pending. Integration AC09 APPROVED, checkpoint canonical update, squash merge and read-back only in a subsequent authorized audit step.
## TESTS
`python scripts/validate_sources.py`; `python -m unittest discover -s tests -v`; `git diff --check`; inspect ZIPs/hashes, negative tests, repo diff and secret scan without logging secret values; run CI only if zero additional cost is proven. No lint/typecheck/build of nonexistent domain code (N/A with reason). Check CI status actual head, settings and billing read-back. Test no mutation of upstream snapshots.
## DELIVERABLES
Branch `work/nle-bootstrap-001`, commit/push, draft PR titled `NLE-BOOTSTRAP-001: Source Pack & Governance`, exact Evidence Bundle (base/head, docs/diff, tests/results, risk, cost, settings, blockers, correction history, checkpoint delta), context lock, audit review pt-BR. Preserve remote PR if already exists; use same ID and CD-xx.
## REVIEW FORMAT
Resumo, Source Check SHA/branch/PR, decisões, AC01–AC09 with PASS/FAIL/BLOCKED/NOT_RUN and evidence, checks, security/cost, risks, errors corrected, diffs, proposed checkpoint delta, verdict. Executor does not declare independent APPROVED.
## STOP CONDITION
Stop on unknown target, billing, governance, access, conflicting approved decision, secret leak, failed gate, or after draft PR/evidence. Do not merge or start INFRA-WO-001. Only independent audit may promote checkpoint and merge with all gates met.

## Delta CD-02 | execução no alvo existente (2026-11-26)
- Branch existente `chore/nle-bootstrap-001`; PR #1 draft; base `48d3e422313f869992d09b99f0b7e09acd4e1caa`. Não criar branch ou PR concorrente.
- NLE-ADR-BOOT-007 (RATIFIED_DIRECTION) supersede o gate private-only **somente** para planejamento/desenvolvimento revisado e não sensível durante este bootstrap. Produção permanece privada; sem dados de clientes, segredos, credenciais, deploy ou gasto. As referências originais a alvo privado e "no public repo" são históricas e ficam limitadas por esse delta.
- O Source Pack completo foi importado: 364/364 originais, seis ZIPs, `locks/source-lock.json`, validadores e testes canônicos. O Context Lock real está em `locks/context-lock.json`.
- Governança: `main` com PR obrigatório, histórico linear, squash-only, sem force/delete, sem bypass e conversas resolvidas; checks obrigatórios e CI pendentes de prova de billing/plano. Nenhum workflow foi ativado.
- Não fazer merge, não promover checkpoint e não iniciar NLE-INFRA-WO-001. Auditoria independente obrigatória.
