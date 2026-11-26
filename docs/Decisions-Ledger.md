# Decisions Ledger

States: RATIFIED_DIRECTION, PROPOSED, APPROVED (after independent audit), BLOCKED, SUPERSEDED. No implementation approval inferred.
| ID | State | Decision |
|---|---|---|
| NLE-INT-PLAN-001 | RATIFIED_DIRECTION | Six memories, hybrid RAG, relational graph, controlled learning; INT-ADR-001..008 preserved |
| NLE-INFRA-PLAN-001 | RATIFIED_DIRECTION | Oracle ARM64 + Windows, WireGuard, PostgreSQL, quotas and official Codex; INFRA-ADR-001..010 preserved |
| NLE-CC-PLAN-001 | RATIFIED_DIRECTION | 35 surfaces, reuse Paperclip; CC-ADR-001..007 preserved; integration conditional |
| CC-ADR-003 | RATIFIED_DIRECTION | Obsidian / Neon Glass, responsive and accessible |
| NLE-BASELINE-001 | PROPOSED | Preserve 105/92/1110/62/35; no runtime approval |
| ADR-SR-001..005 | PROPOSED | Registry, locks, quarantine, permissions, releases |
| WF-ADR-001..005 | PROPOSED | Default deny, event ledger, segregation |
| NLE-ADR-BOOT-001 | PROPOSED | Immutable snapshots and fingerprints |
| NLE-ADR-BOOT-002 | PROPOSED | Single sequential backlog preserving 40 IDs |
| NLE-ADR-BOOT-003 | PROPOSED | Plugin vs private sidecar decision at CC-WO-001 via qualified PoC; no initial fork |
| NLE-ADR-BOOT-004 | PROPOSED | Security and US$0 fail closed; reuse native controls |
| NLE-ADR-BOOT-005 | PROPOSED | Planning grants no execution, access, spend or skill promotion |
| NLE-ADR-BOOT-006 | RATIFIED_DIRECTION | Target changed from NexLabsTech/nexlabs-enterprise to KayzenRoot/nexlabs-pipeline |
| NLE-ADR-BOOT-007 | RATIFIED_DIRECTION | Owner authorizes temporary public repository for reviewed non-sensitive planning/development, superseding private-only repository gate during this phase; private production unchanged. No client data, secrets or credentials in Git. No approval to deploy or spend. |

NLE-ADR-BOOT-007 is a narrow owner-authorized delta. Preserve historical decisions and snapshots unchanged. Recheck visibility at each integration; private conversion does not erase previous public copies. The original complete ledger and decision index must be reconciled at full import; do not treat this partial import as independent approval.
