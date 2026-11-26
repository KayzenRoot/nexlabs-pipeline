# NLE-INFRA-WO-001 | Infrastructure inventory and local-first Paperclip

**Status:** ACTIVE — **CD-02 LOCAL FIRST**, owner-ratified on 2026-11-26. The CD-01 read-only inventory below is preserved as historical sub-scope; see **Delta CD-02** at the end.
**Risk:** ELEVATED for local Paperclip installation; runtime is BLOCKED while Docker Desktop is absent.
**Repository:** KayzenRoot/nexlabs-pipeline
**Base SHA:** 8321110a2ff29aec90ffc1c384ea21f722de0497
**Branch:** work/nle-infra-wo-001

## OBJECTIVE
Build and execute a strictly read-only inventory of the existing Oracle Ubuntu ARM64 VPS and Windows 11 execution host, then qualify Paperclip deployment and execution compatibility from measured evidence. This is the first infrastructure gate, not an installation.

## CONTEXT
The owner explicitly authorized this previously blocked first increment. Canonical architecture identifies:
- Oracle Ubuntu 24.04 ARM64 as the candidate control plane for Paperclip and the Intelligence Hub.
- Windows 11 as the candidate execution plane for the official Codex CLI, builds and E2E.
- WireGuard as the private-network direction, not yet installed or qualified.
- Paperclip as the operational source of truth for agents, hierarchy, tasks, projects, goals, runs, approvals and recorded costs.
- Git as the source of code, policies, decisions and approved skills.
- A target catalog of 105 agents, 92 packages, 1,110 assignments, 1,071 contextual competencies, 62 workflows and 35 UI surfaces. These are planned identities/capabilities, not grants or active agents.
- Initial global LLM concurrency 1, no paid fallback, additional spend USD 0, heartbeats and workflows disabled, and external effects denied.

Official Paperclip references consulted 2026-11-26:
- Docker deployment guide: https://docs.paperclip.ing/reference/deploy/docker/
- Runner compatibility: https://docs.paperclip.ing/reference/adapters/paperclip-runner/
- Remote environments: https://docs.paperclip.ing/experimental/environments/
- Agents API: https://docs.paperclip.ing/reference/api/agents/
The current documentation describes Docker deployment and required session/action-signing secrets; Runner support on Linux ARM64 requires GNU libc 2.39 or newer, while Windows remains on the legacy runner. Remote SSH/Sandbox environments are experimental. These are compatibility facts to verify against the actual target, not permission to enable experimental features.

## SCOPE
1. Add read-only VPS and Windows inventory collectors.
2. Add deterministic tests for script syntax and forbidden side effects/secret access.
3. Execute the collectors on the actual VPS and Windows host through an already-authorized SSH path and local PowerShell.
4. Measure OS/architecture/libc, CPU/RAM/swap, filesystem/inodes, Docker/Compose and running container resource usage, listening TCP bind scopes, relevant service state, WSL, Codex CLI status, Git, Docker and Windows hardware/volume capacity.
5. Classify Paperclip control-plane image compatibility, Runner compatibility, Windows execution options, resource headroom, network exposure and unknowns.
6. Produce a redacted evidence summary suitable for this public development repository. Raw host reports stay local and must not be committed.

## OUT OF SCOPE
- Installing, upgrading, starting, stopping or reconfiguring Paperclip, Docker, PostgreSQL, WireGuard, 9Router, Netdata, Portainer, WSL or any agent runtime.
- Creating accounts, users, SSH keys, credentials, tokens, secrets, API connections or billing changes.
- Opening ports, changing OCI security lists/NSGs, firewall rules, DNS, network interfaces, volumes, swap, Docker networks or service definitions.
- Deploying, activating, importing/hiring agents, enabling skills, workflows, routines, heartbeats, schedules, external effects or LLM calls.
- Reading .env, environment-variable values, secret stores, SSH private keys, credential files, process command lines, logs, browser cookies, provider tokens or raw Codex login output.
- Network scans, external probes, paid services, public exposure, real customer data or financial operations.
- Paperclip DB writes or direct edits to Paperclip-owned tables.

## FILES / SOURCES TO READ
- docs/Checkpoint.md, docs/Decisions-Ledger.md, docs/Scope.md, docs/Definition-of-Done.md
- docs/Architecture.md, docs/Requirements.md, docs/Security.md, docs/Backlog.md
- sources/NexLabs_Infrastructure_Plan/README.md
- sources/NexLabs_Infrastructure_Plan/{infra-qualification.json,runtime-policy.json,agent-runtime-bindings.json,workflow-runtime-bindings.json,skill-runtime-bindings.json,source-lock.json}
- sources/NexLabs_Command_Center_Plan/README.md and decisions.md
- scripts/infra/collect_vps_inventory.sh, scripts/infra/collect_windows_inventory.ps1, tests/test_infra_inventory.py

## REQUIREMENTS
- REQ-02: Paperclip remains operational source of truth; never write its internal DB.
- REQ-04: USD 0 incremental; unknown provider/feature cost blocks activation.
- REQ-07: private network and least privilege; no global mounts or credentials.
- REQ-11: actual VPS/Windows compatibility, recovery prerequisites and resource headroom must be evidenced.
- REQ-12: stable WO, Context Lock, tests, CI, Evidence Bundle, independent audit and checkpoint delta.
- Every collector must be non-interactive, best-effort, read-only and safe when optional tools are absent.
- Raw inventory may contain infrastructure-sensitive metadata. Keep raw reports outside Git; publish only redacted PASS/FAIL/UNKNOWN findings and report digests.
- Distinguish measured host facts from official documentation, assumptions and unverified OCI/account facts.

## ARCHITECTURE RULES
- VPS is a candidate control plane, not presumed qualified.
- Windows is a candidate execution plane; do not assume native Windows Paperclip Runner support.
- Paperclip Docker standard image architecture and exact digest must be verified before a later install WO.
- Linux ARM64 Runner requires glibc >=2.39 according to current official docs; verify actual libc.
- Remote SSH/Sandbox execution is experimental; no activation in this WO.
- No PostgreSQL, Redis, Kafka, Neo4j, Kubernetes, 9Router or vector database installation in this increment.
- No more than one global LLM slot; all provider costs/quotas unknown until officially read back.

## CONSTRAINTS
- No host shell/SSH connection is available to this ChatGPT execution context. Actual host execution must use the user's already-authorized local Codex/SSH environment; do not pretend a repository CI runner is the user's VPS or PC.
- The VPS collector must be streamed over SSH stdin; do not copy it to the server or write a report there.
- If a unique existing SSH alias cannot be identified, stop and ask the owner; do not guess a host/IP or inspect private keys.
- Do not print or commit hostnames, public/private IPs, usernames, SSH paths, container names, raw command output or secrets in public Git evidence.
- Do not use sudo, alter firewall/NSG, change resources or install packages.
- No merge, deployment, Paperclip onboarding, agent import or runtime activation in this WO.

## ACCEPTANCE CRITERIA
- AC01: VPS Bash collector passes bash -n and has no mutating commands, external network probes, file writes or credential reads.
- AC02: Windows PowerShell collector has no mutating commands, network probes, file writes, environment-variable dumps or raw credential output.
- AC03: automated tests prove the safety invariants and existing Source Pack validation remains intact.
- AC04: actual VPS report confirms or rejects Ubuntu/architecture/glibc, CPU/RAM/swap/disk/inodes, Docker/Compose, containers, listener bind scopes, WireGuard presence and service state.
- AC05: actual Windows report confirms or rejects OS/build, CPU/RAM/GPU, disk headroom, WSL, Docker, Codex CLI/login status, Git/SSH and listening bind scopes.
- AC06: Paperclip image architecture/digest, Runner compatibility, remote execution constraints and resource caps are classified with evidence; OCI NSG/security-list and billing/quota state remain UNKNOWN unless separately read back from the authorized console.
- AC07: raw reports remain local; committed Evidence Bundle contains only redacted findings and SHA-256 digests.
- AC08: GitHub CI passes on the exact PR head; no secrets or host details appear in diff/logs.
- AC09: independent audit is APPROVED, Checkpoint Delta is promoted only after audit, and merge occurs only after all required gates and owner authorization.

## TESTS
- bash -n scripts/infra/collect_vps_inventory.sh
- python3 -m unittest discover -s tests -v
- python3 scripts/validate_sources.py
- Static scan for install/start/stop/restart/firewall/network-probe/file-write/secret-read commands.
- Actual read-only target execution on VPS and Windows; verify collector safety and redaction.
- Compare measured values against INFRA-Q01..Q07; remaining 32 scenarios stay NOT_RUN and are not claimed as qualified.

## DELIVERABLES
- Read-only VPS and Windows collectors.
- Automated safety/syntax tests.
- Local raw reports stored outside repository.
- Redacted evidence/NLE-INFRA-WO-001-CD01-SUMMARY.md with report SHA-256 values and PASS/FAIL/UNKNOWN only.
- Context Lock with actual Git base/head and canonical fingerprints.
- CI evidence, audit result in pt-BR and proposed Checkpoint Delta.
- Draft PR NLE-INFRA-WO-001: read-only infrastructure qualification.

## REVIEW FORMAT
Resumo; Source Check/base/head; Context Lock freshness; AC01–AC09 PASS/FAIL/BLOCKED/NOT_RUN; VPS/Windows measurements; Paperclip image/Runner/remote-environment compatibility; security/cost; tests and CI; raw-report digests; redacted diff; risks; verdict APPROVED / CORRECTION REQUIRED / BLOCKED.

## STOP CONDITION
Stop on missing or ambiguous SSH access, unexpected mutation requirement, secrets in output, unverified cost, insufficient resource headroom, unsupported architecture/libc, host mismatch, failed test, stale Context Lock or HIGH/CRITICAL finding. Do not install Paperclip or proceed to the next WO.

## NEXT DEPENDENCY
After this WO is APPROVED, the canonical backlog's next increment is NLE-SR-WO-001 (registry schema, locks, quarantine and validator), followed by NLE-INFRA-WO-002 (private network, identity, secrets and isolation), NLE-WF-WO-001 (event/authorization/ledger contract), and then NLE-INFRA-WO-003 (Paperclip + PostgreSQL deployment and initial backups). Paperclip installation is deliberately not pulled into this read-only WO.

## Delta CD-02 | LOCAL FIRST (owner-ratified 2026-11-26)

**Decision:** NLE-ADR-INFRA-011. This delta supersedes only the CD-01 prohibition on installing Paperclip locally. The CD-01 read-only inventory and its collectors remain preserved as history/subscope. VPS access, SSH, firewall/NSG/DNS changes, remote deploy, agents, API keys, subscriptions, spend and external effects remain out of scope.

### Objective CD-02
Install and validate the first functional Paperclip instance **locally on this Windows 11 host**, before any VPS Oracle deployment, with a portable composition prepared for future Ubuntu ARM64 operation. If a prerequisite requires an unauthorized administrative action, stop with the exact action and do not install it.

### Local architecture
- Windows 11 host; Docker Desktop with WSL2 backend; Linux containers.
- Official self-hosted Paperclip image `ghcr.io/paperclipai/paperclip:2026.1117.0@sha256:bdf38d10544dc6c831e16dc027f23ad586353ef3be1a1b2c6979e63b956aceb1` (OCI index with `linux/amd64` and `linux/arm64`).
- Embedded PostgreSQL in the quickstart, persistent under the data mount; no separate PostgreSQL install locally.
- VPS future: external PostgreSQL 17 pinned by digest, same Paperclip image, private access, independent secrets and logical migration.
- Access only `http://localhost:3100`; bind must be `127.0.0.1:3100`.
- Codex CLI via the official Paperclip `codex_local` mechanism, using subscription authentication when the owner authorizes it in the browser; no API key and no copying of personal auth files.

### Security and data
- Generate `BETTER_AUTH_SECRET` and `PAPERCLIP_TOOL_ACTION_SIGNING_SECRET` with a CSPRNG; store outside Git in a protected persistent directory; never print, log or commit values.
- `.gitignore` must cover local data, backups, env files, keys and restore artifacts.
- No `latest` tag without digest; no Cloud image variant; no agent execution; no heartbeats, routines, workflows, external effects, provider API keys or billing changes.
- Do not use `docker compose down -v` or delete volumes; stop containers gracefully and preserve data.

### Acceptance criteria CD-02
- AC10: decision, backlog, work order and Context Lock updated; previous lock marked STALE; new lock generated.
- AC11: portable compose and image lock with immutable index digest and verified `linux/amd64`/`linux/arm64` manifests.
- AC12: local Windows configuration binds only `127.0.0.1:3100`, with embedded PostgreSQL persistence and healthcheck.
- AC13: protected local secrets created outside Git; no secret values in repository, logs or evidence.
- AC14: PowerShell initialization, start, safe stop, status and backup scripts exist and pass offline safety tests; no `down -v`.
- AC15: Paperclip starts locally, `/api/health` passes, data persists across restart, backup and restore are validated. **BLOCKED if Docker Desktop is absent; do not install it without owner authorization.**
- AC16: Codex integration prepared using the official mechanism, without API key and without reading/copying personal auth files.
- AC17: VPS composition prepared with external PostgreSQL 17 pinned digest and ARM64 compatibility; no VPS access, SSH or deploy.
- AC18: catalog 105/92/1110/1071/62/35 preserved; no agent import, hiring, heartbeat, workflow or external effect.
- AC19: Source Pack validator, existing tests, deployment tests, secret scan and GitHub CI pass on the exact head; Evidence Bundle, audit and Checkpoint Delta are produced. No merge without independent APPROVED and owner authorization.

### Tests CD-02
- Static compose/YAML validation, image lock consistency, port bind checks and forbidden-command scans.
- PowerShell offline self-test: secret file creation/ACL (without printing), backup/restore into an isolated directory, integrity hash, port check.
- If Docker is available: `docker compose config`, image architecture inspection, start, healthcheck, persistence/restart, backup/restore, localhost-only exposure.
- `python3 scripts/validate_sources.py`; `python3 -m unittest discover -s tests -v`; GitHub CI `docs-validation`.

### Stop conditions CD-02
Stop without installing or reconfiguring if Docker Desktop/WSL2 is absent or requires administrator privileges not authorized; the image lacks the required architecture; port 3100 is occupied without a safe alternative; a secret would be exposed; data loss risk; authentication requires human action; a subscription/spend is required; or any HIGH/CRITICAL risk appears.
