# NLE-SR-WO-001/CD-01 — Registry foundation and dry-run provisioner

OBJECTIVE: implement deterministic offline registry compilation, specification manifests, agent locks, quarantine, strict validation and 105-agent provision intentions.

CONTEXT: PR #3 approved/merged; checkpoint PR #4 merged/read-back at 05764c3d8e3050ddec9e4b8a010232f150704acb. ADR-SR-001..005 are proposed; this increment implements only conservative offline contracts under explicit owner authorization, without ratifying production behavior.

SCOPE: schema envelopes, Python stdlib compiler and verifier, deny-all policy, exact source-lock fingerprint, 92 manifests, 105 agent locks, all 1110 assignments/1071 competency records, 17 external quarantines + OWN authoring, topological dry-run with CEO reconciliation, automated regression tests, CI.

OUT OF SCOPE: SKILL.md creation/import, external source download, live Paperclip API/DB access, model calls, credential grants, installation, enabling agents or heartbeats, VPS, paid services, next WO.

FILES/SOURCES TO READ: canonical hierarchy and source paths recorded in locks/NLE-SR-WO-001-context-lock.json; sources/NexLabs_Skills_Registry/README.md; registry/policy.json; registry/core.py; tests/test_registry.py.

REQUIREMENTS / ARCHITECTURE: Git is canonical; Paperclip remains runtime authority; source artifacts immutable; actual permissions deny by default; specification hash is not artifact qualification; runtime IDs/model/adapter unresolved. No duplicate Zeus; future provisioner must reconcile verified identity before create. C12, post-auth backup, least-privilege grants and owner authorization stay gates.

CONSTRAINTS: USD 0 additional, stdlib only, no secrets, no network, no source changes, no force-push/bypass. No real execution.

ACCEPTANCE CRITERIA:
AC01 baseline lock and all original sources validated.
AC02 92 specification manifests, 105 locks, 1110 assignments, 1071 contextual competencies, 183 links, 316 individual test references preserved.
AC03 17 external sources quarantined, OWN requires authoring, no executable artifact or grant.
AC04 deterministic JSON; fail closed on drift, duplicate IDs/keys, path traversal, symlinks, dependencies/cycles and unsafe policy.
AC05 plan includes 105 topologically ordered paused intentions, zero actual creates/updates/model calls; existing Zeus requires reconciliation.
AC06 tests, existing canonical validator, focused scanner and required CI pass.
AC07 independent review of exact head, evidence and checkpoint delta; no merge until APPROVED.

TESTS: python -m registry verify; python -m unittest discover -s tests -v; python scripts/validate_sources.py; python scripts/security/scan_repository.py.

DELIVERABLES: registry compiler, policy, schema envelopes, CLI, tests, Context Lock, same WO PR/evidence. REVIEW FORMAT: pt-BR, base/head, AC01-07, counts, security, CI, risks/verdict.
STOP CONDITION: failed check or unresolved HIGH/CRITICAL, stale lock, new spend, unauthorized effect; no next WO until approved and merged.
