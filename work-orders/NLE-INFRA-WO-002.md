# NLE-INFRA-WO-002/CD-01 — Offline security control contracts

**Classification:** NECESSARY  
**Risk:** HIGH_ASSURANCE  
**Parent:** NLE-INFRA-WO-002 (private network, identity, secrets and isolation)  
**Base:** `eebbd7325ab45fca8e176bd713245189ed148bdd`

## OBJECTIVE
Implement a real, deterministic, technology-neutral security control library for identity, least-privilege authorization, independent approval verification, private-network policy validation, opaque secret references and tenant/workspace isolation. This is the first offline slice of NLE-INFRA-WO-002, not a live network or runtime deployment.

## CONTEXT
NLE-SR-WO-001/CD-01 is APPROVED and merged; checkpoint PR #6 is read back at the base above. The canonical Infrastructure Plan requires default-deny, exact grant intersection, private network boundaries, no credential copying, isolated workspaces, owner-bound approvals and US$0. WireGuard/INFRA-ADR-003 and the other INFRA ADRs remain PROPOSED. Do not silently ratify them. Existing Windows secret generation and owner-only ACL helpers are in `scripts/windows/Paperclip.Common.ps1`; reuse/audit their contract, do not duplicate or execute them. The VPS is explicitly outside this increment.

## SCOPE
- Standard-library-only Python package `security/`.
- Immutable principal, resource scope, grant and authorization request contracts. The principal is a trusted adapter input; this slice does not authenticate live Paperclip/user identities.
- Fail-closed policy evaluation requiring exact principal/task/tenant/project/workflow/skill/host/provider/risk/policy/epoch intersection; no hierarchy or CEO bypass.
- Approval envelope verifier binding actor, independent human approver, action, target, tenant, payload hash, policy hash, evidence, zero-spend ceiling, expiry and one-time nonce. A pluggable verifier contract; HMAC-SHA256 adapter is test-only and not selected as production trust architecture.
- Generic private-network descriptor validator: private/loopback addresses only, no wildcard/public bind, no default route, unique peer identities, no live config generation.
- Opaque, version-pinned SecretRef validation only; no secret value resolution, provider implementation or secret creation/rotation.
- Tenant equality and safe workspace path confinement; reject traversal, symlink and Windows reparse points.
- Deterministic CLI, policy/schema docs, synthetic tests and CI.

## OUT OF SCOPE
WireGuard installation/configuration or key generation; VPN, firewall, NSG, DNS, SSH, port or host changes; any VPS or local Windows runtime access; live Paperclip API/DB, identity sync, grants or mutations; secret retrieval/rotation or OAuth; signing-key provisioning; durable nonce/event ledger (owned by NLE-WF-WO-001); Docker socket, host mounts, agent/heartbeat/workflow activation; model calls, external effects, production deployment, new spend.

## FILES/SOURCES TO READ
`locks/NLE-INFRA-WO-002-context-lock.json`; `docs/Checkpoint.md`; `docs/Decisions-Ledger.md`; `docs/Scope.md`; `docs/Definition-of-Done.md`; `docs/Architecture.md`; `docs/Requirements.md`; `docs/Security.md`; `docs/Backlog.md`; `sources/NexLabs_Infrastructure_Plan/README.md` §§2,6,9–12; `runtime-policy.json`; `infra-qualification.json`; agent/workflow/skill runtime bindings; `registry/policy.json`; `scripts/windows/Paperclip.Common.ps1`; `Initialize-PaperclipSecrets.ps1`; deployment compose files and existing deployment tests.

## REQUIREMENTS / ARCHITECTURE RULES
1. Default deny, exact scope intersection, no inherited grants and no privileged role bypass.
2. Tenant/project isolation applies to every request; unknown, stale, revoked, expired or mismatched claims deny.
3. HIGH_ASSURANCE requires an independent human approver with an authorized OWNER/AUTHORIZED_REVIEWER role, bound payload/policy hashes, evidence, expiry, zero spend and replay-resistant nonce verification.
4. Every effect other than explicitly internal-only is denied. Maximum additional spend is exactly USD 0.
5. Network policy must reject public/wildcard/default routes. WireGuard remains an unselected candidate until its ADR is ratified.
6. Secret references contain identifiers/metadata only. Secret values and signing keys never enter Git, fixtures, logs or agent context.
7. Workspaces remain inside their tenant/project/task root; reject traversal and link/reparse components.
8. No network, environment credential lookup, subprocess, filesystem mutation, runtime client or non-standard dependency.
9. HMAC verifier exists solely as a deterministic test adapter. Production verifier/key custody is a separate unresolved integration gate.
10. Durable nonce consumption and event/approval ledger belong to NLE-WF-WO-001; in-memory nonce storage is test-only.

## CONSTRAINTS
US$0 additional; standard library only; no API keys; no secrets; no live network; no VPS/SSH; no Paperclip writes; no agent or skill activation; no force-push, bypass or destructive action. Source Pack is immutable.

## ACCEPTANCE CRITERIA
- AC01 Context Lock matches base and all critical source blobs; 364 Source Pack files unchanged.
- AC02 Principal, request, grant and policy validation are strict and fail closed.
- AC03 Grant decision checks every exact scope dimension, epoch, revocation, expiry, tenant/project and zero-cost policy.
- AC04 HIGH_ASSURANCE approval binds actor/approver/action/target/tenant/payload/policy/evidence/expiry/nonce; rejects self-approval, invalid signature, replay and any nonzero cost.
- AC05 Network descriptor accepts only explicitly RFC1918/ULA/loopback ranges and rejects public/special-purpose, wildcard, default route, invalid port and duplicate peer/key reference.
- AC06 SecretRef is opaque, version-pinned and tenant/purpose scoped; no secret resolution exists.
- AC07 Workspace resolver rejects cross-tenant, traversal, symlink and reparse paths without creating or modifying directories.
- AC08 100% targeted tests, canonical source validator, Registry verification, security scan, SonarCloud and required Linux CI and Windows junction CI pass; no HIGH/CRITICAL.
- AC09 Independent audit APPROVED on exact final HEAD; checkpoint delta proposed only after approval.

## TESTS
`python -m security verify`; `python -m unittest discover -s tests -v`; `python3 scripts/validate_sources.py`; `python3 -m registry verify`; `python3 scripts/security/scan_repository.py`. Tests use synthetic identities, fake HMAC key in memory and temporary directories only.

## DELIVERABLES
Security contracts/library, policy and JSON schemas, deterministic CLI, tests, README, Context Lock, Evidence Bundle and PR. Review in pt-BR with proof obligations, exact SHAs, tests, CI, residual risks and verdict.

## REVIEW FORMAT
APPROVED / CORRECTION REQUIRED / BLOCKED. Distinguish offline contract proof from live network, credential, runtime or deployment qualification. No claim of operational private networking or production secret custody.

## STOP CONDITION
Any HIGH/CRITICAL, failed test/check, stale Context Lock, source drift, unapproved ADR dependency, nonzero spend, secret exposure, network/VPS/runtime mutation or missing independent review blocks merge and all subsequent WOs.


## Executor evidence (not approval) | 2026-11-26
Candidate HEAD before evidence refresh: `cbb82ad3d9ac6c6ab3f3dc79dc116a48b6a22149`; CI run 45899962882 SUCCESS. Linux 91 tests (2 platform skips); Windows 38/38 including junction; source validator and Registry pass; scanner 471/0; Socket and ECC evidence pass. SonarCloud Quality Gate passed, but 11 new issues remain open, 0 Security Hotspots and 0.0% coverage on new code. Their severity/rule details are not yet retrieved, so AC08 and independent AC09 remain pending. No merge, checkpoint promotion or next WO. See `evidence/NLE-INFRA-WO-002-CD01-EXECUTION.md`.
