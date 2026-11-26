# NLE-INFRA-WO-001/CD-03 — Final runtime audit and correction record

Date: 2026-11-26
Repository: `KayzenRoot/nexlabs-pipeline`
PR: #3 (draft, branch `work/nle-infra-wo-001`)
Base: `8321110a2ff29aec90ffc1c384ea21f722de0497`
HEAD at source check: `b7f447dcbdb807aa3028150e9f33e0406c42d212`
Scope: local Windows 11 / Docker Desktop / Paperclip only. No VPS, SSH, deploy, agent task, workflow, API key or spend.

## 1. Source Check

- Fetched the existing PR branch and fast-forwarded to the expected HEAD `b7f447d`; no new branch or PR was created.
- Worktree was clean before the CD-03 corrections. The corrections and this evidence are appended to the same PR.
- Published CD-02 corrections and the ratified 105-agent/92-package/1110-assignment/62-workflow/35-screen catalog remain preserved.
- The prior CD-01 Context Lock remains `STALE` under `locks/history/`; it was not overwritten.

## 2. Fresh runtime read-back

| Check | Result |
|---|---|
| Docker Desktop / engine | 4.100.1 / 29.9.3, WSL2 backend |
| Compose project / container | `nexlabs-paperclip` / `nexlabs-paperclip-paperclip-1` |
| Container ID | `15d16428468e31993dd2f9992dc79845509ccd74c9ecb46630a3e3fdd2e93a1a` |
| Image | `ghcr.io/paperclipai/paperclip:2026.1117.0@sha256:bdf38d10544dc6c831e16dc027f23ad586353ef3be1a1b2c6979e63b956aceb1` — matches image lock |
| State | `running` / `healthy` |
| Port | `127.0.0.1:3100->3100/tcp`; listener only on `127.0.0.1` |
| Health | HTTP 200; `status=ok`, `deploymentMode=authenticated`, `deploymentExposure=private`, `bootstrapStatus=ready` |
| Claim | **PASS** — pre-claim state was `bootstrap_pending`; now `ready` |
| Database backup status | `ok` (Paperclip health field) |

`Get-PaperclipStatus.ps1` now asserts the exact Compose container and pinned image before reporting health. An unrelated service returning HTTP 200 is rejected with `PORT_IN_USE_UNRELATED_SERVICE`, `PAPERCLIP_CONTAINER_NOT_FOUND`, `PAPERCLIP_IMAGE_MISMATCH` or `PAPERCLIP_CONTAINER_NOT_HEALTHY`.

## 3. Blocking finding — Codex subscription auth is not valid

Owner confirmation was treated as a claim to verify, not as proof. Read-only runtime evidence contradicts it:

- `codex login status` inside the container returns **“Not logged in”**, both with the default home and `CODEX_HOME=/paperclip/.codex`.
- No Codex auth file exists under `/home/node/.codex` or `/paperclip/.codex`; only ephemeral `.codex/tmp/arg0-linux` helpers exist.
- Database audit (read-only, no secret values printed): `adapter_auth_sessions` has 3 rows, all `adapter_type=codex_local`, all `status=cancelled`; `result_claim`, `connection_id` and `grant_id` are null. Sessions were created/updated between 18:34:53 and 18:38:46 UTC.
- `ai_subscription_connections=0`, `ai_connection_pools=0`, `ai_provider_defaults=0`, `tool_connections=0`.
- One default agent row exists (`Zeus`, `codex_local`, `status=paused`, created 18:34:46 UTC). It was created as a side effect of the owner claim/bootstrap; it has not run. No agent-task/run tables contain rows.
- The agent `adapter_config` contains only non-auth Codex sandbox settings (no model, provider, connection or token field).

Consequence: **AC16 is not met**. No agent task was executed, no API key was created, and no auth file was copied. Codex-dependent execution remains blocked until the owner completes a successful login through the Paperclip UI and the container reports an authenticated Codex status. Owner confirmation must not be recorded as verified auth.

## 4. Corrections applied

1. **Restore isolation (HIGH):** `Restore-Paperclip.ps1` now requires a new direct-child `restore-test-*` target, rejects existing targets, external/ancestor paths and reparse-point ancestors, and rejects `-Force`. The guard runs before extraction. `Expand-PaperclipBackupArchive` also rejects `-Force`, requires a SHA-256 sidecar and verifies it before extraction.
2. **Hidden files and backup coverage:** backups use .NET `ZipFile` with `Get-ChildItem -Force -Recurse`, so hidden files and nested hidden directories are included. Ephemeral `.codex/tmp` sandbox helpers are excluded. The SHA-256 sidecar is mandatory.
3. **Restored permissions:** a one-off pinned-image container repairs Linux ownership/mode (`0700`) on the restored data before it is used; the restored copy is never started with real credentials during isolation tests.
4. **Container identity:** health/startup/status verify the Compose project, exact pinned image and healthy state, preventing false positives from an unrelated HTTP 200 on port 3100.
5. **SonarCloud:** all 10 reported findings were fixed individually in `collect_windows_inventory.ps1` (6 empty catches now assign explicit `NOT_AVAILABLE`/`UNKNOWN`) and `collect_vps_inventory.sh` (positional parameter, `[[` tests, `NOT_AVAILABLE` constant). No issue was excluded or marked false-positive.
6. **ECC evidence:** `evidence/NLE-INFRA-WO-001-CD03-SECURITY-EVIDENCE.md` provides focused security evidence for the flagged surface; no permissions were expanded.
7. **Docker eligibility/cost:** Docker Desktop personal plan, no organization membership and no paid subscription observed; no paid runner/API/service was used. Commercial-size eligibility still requires owner attestation.
8. **Operational docs and Work Order:** updated to state claim PASS, Codex auth FAIL, and the no-activation boundary.

## 5. Tests

| Test | Result |
|---|---|
| `python scripts/validate_sources.py` | 7/7 groups PASS (364 sources, 6 ZIPs, 105 agents, 62 workflows, 40 WOs) |
| `python -m unittest discover -s tests -v` | **29/29 OK** |
| `Test-PaperclipDeployment.ps1` (offline) | **43/43 PASS**, 0 FAIL |
| `docker compose ... config --quiet` (base + local) | exit 0 |
| `bash -n scripts/infra/collect_vps_inventory.sh` | PASS |
| PowerShell parser, all `scripts/windows/*.ps1` | 0 errors |
| Git diff check | clean (no whitespace errors) |

The PowerShell suite covers existing targets, active directories, external paths, `-Force`, missing/tampered sidecars, hidden files, nested hidden directories and a real Windows junction (`RESTORE_ROOT_REPARSE_POINT`), plus live-data immutability (`live_sentinel_unchanged`). Static assertions are not presented as runtime proof; the runtime backup/restore was executed separately.

## 6. Backup and database consistency

- Post-claim cold backup: `paperclip-data-20261126T185859Z-42fb1281.zip`, SHA-256 `933a478e8d5660da2e4ddfc677eb67680253c2eb37f45e94c913fb55a0d8cb00`, 4,723 entries.
- The archive includes hidden ownership markers, `instances/default/ai-local-logins/`, `instances/default/secrets/master.key`, `decision-signing.key`, `PG_VERSION` and `postgresql.conf`. It may contain account/session state and is therefore kept in the protected backup directory with owner-only ACL, outside Git.
- PostgreSQL was stopped gracefully for the cold copy; the internal `pnpm db:backup` reports `ok`. An isolated restore verified SHA-256, file count/size and required files with permissions repaired, and was **not started**. No restored instance ran with real credentials.
- Pre-claim isolated restore was started on a separate port and returned health 200; that result is retained as historical runtime evidence, not as proof of the Codex-authenticated state.

## 7. SonarCloud and ECC

- The public SonarCloud API returned 10 open issues for PR #3. Each has a code-level fix in this candidate (table in the security evidence). Final API read-back at the pushed HEAD is required; the quality gate is not inferred from silence.
- ECC Tools raised a predictive `action_required` alert on `deploy/local/agents/README.md`. The focused security evidence and new regression tests respond to it. Check publication depends on the ECC app's Checks permission; this Work Order did not expand integration permissions.

## 8. Context Lock

- All SHA-256 fingerprints for the canonical file set were recalculated from the corrected working tree and recorded in `locks/NLE-INFRA-WO-001-context-lock.json`.
- Historical CD-02 SHA-256 values and Git blob identities are retained for provenance; they are not presented as current.
- The lock cannot contain its own final commit hash; final HEAD and CI are verified externally after push.

## 9. Residual risks and blockers

1. **BLOCKER:** Codex subscription auth is absent/cancelled; AC16 cannot pass until owner re-authentication succeeds.
2. One paused default agent exists as a claim side effect; it must remain paused and unexecuted until separate authorization.
3. Docker Desktop commercial eligibility requires owner attestation of organization size; no paid plan was purchased.
4. Backups contain claim/session state and secret keys; they must remain private and never be committed or shared.
5. C: free space is low (~9.9 GiB at last check); monitor Docker growth.
6. Independent read-only audit of the final pushed HEAD is still required.

## 10. Verdict

**NOT APPROVED — BLOCKED ON CODEX AUTHENTICATION.**

The infrastructure corrections, restore isolation, hidden-file backup coverage, container identity checks, local bind, claim read-back and test suite pass. The runtime does not have valid Codex subscription authentication, so AC16 is unmet and no agent execution can be qualified. No merge, checkpoint promotion, sprint start, VPS access or additional spend is authorized by this record.
