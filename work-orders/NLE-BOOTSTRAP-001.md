# NLE-BOOTSTRAP-001 | CD-02 partial transfer
## OBJECTIVE
Complete original Source Pack and GitHub governance on existing KayzenRoot/nexlabs-pipeline without new spend.
## CONTEXT
Owner ratified INT, INFRA, CC and Obsidian. Owner authorized temporary PUBLIC development. Base 48d3e422313f869992d09b99f0b7e09acd4e1caa, branch chore/nle-bootstrap-001. Exact partial sources tree 3856ba9b4995443510166cefa5f2550394465be5. Original complete archive required. C01 access/base resolved; remaining gates blocked.
## SCOPE
Verify full Source Pack; preserve exact sources; import missing files and reconcile all candidate canonical docs with full originals, preserving CD-01/CD-02 and NLE-ADR-BOOT-007; no duplicate branch or PR. Context Lock, authorized governance and free CI preflight.
## OUT OF SCOPE
Runtime, infrastructure changes, credentials, real client data, spend, mainnet, trading, ads, publishing externally, deploy or merge. No force push or bypass.
## FILES/SOURCES TO READ
README, checkpoint, ledger, scope, DoD, architecture, requirements, governance, security, audit, backlog, full original sources/locks/validators.
## REQUIREMENTS / ARCHITECTURE RULES
Original REQ-01/02/04/07/12/15 and all preserved IDs; Paperclip runtime; Git canonical; default deny; no third-party runtime. Plugin vs sidecar conditional.
## CONSTRAINTS
US$0; no secret exposure. Public repository exception for reviewed non-sensitive development only; private production. No self-approval.
## ACCEPTANCE CRITERIA
AC01 target/access/base/visibility exception; AC02 all 364 originals and 6 ZIPs; AC03 cross-links/gates/default disabled; AC04 complete canonical docs and 40 WOs; AC05 ratifications/ADRs/conflicts; AC06 Context Lock, CI free, local tests; AC07 governance and squash verified; AC08 draft PR and Evidence Bundle; AC09 independent APPROVED, checkpoint promotion, merge/read-back in separate audit step.
## TESTS
python scripts/validate_sources.py; python -m unittest discover -s tests -v; git diff --check; inspect all hashes, source lock, negative tests and secret hygiene; no CI without proven free quota. No runtime tests claimed.
## DELIVERABLES
Same branch and draft PR; commits, context lock and Evidence Bundle with base/head, changed files, commands/results, security/cost/governance, risks, correction history and proposed checkpoint delta.
## REVIEW FORMAT
Português-BR: resumo, source check, AC01–AC09, testes, evidências, diff, bloqueios, veredito.
## STOP CONDITION
Stop on any failed gate; no merge, no next WO, no self-approval. Original complete Work Order details must be restored with the explicit visibility exception.
