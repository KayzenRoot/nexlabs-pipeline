# NLE-INFRA-WO-001/CD-03 — Final runtime audit and correction record

Date: 2026-11-26
Repository: `KayzenRoot/nexlabs-pipeline`
PR: #3 (draft, branch `work/nle-infra-wo-001`)
Base: `8321110a2ff29aec90ffc1c384ea21f722de0497`
HEAD at source check: `cbe49a8b9c2a97a1ad9bcb534cd9faaf1337a176`
Scope: local Windows 11 / Docker Desktop / Paperclip only. No VPS, SSH, deploy, agent task, workflow, API key or spend.

## 1. Source Check

- Fetched the existing PR branch and confirmed the expected HEAD `cbe49a8`; no new branch or PR was created.
- Worktree was clean before the auth-gate evidence changes. The corrections and this evidence are appended to the same PR.
- Published CD-02/CD-03 corrections and the ratified 105-agent/92-package/1110-assignment/62-workflow/35-screen catalog remain preserved.
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

## 3. Codex subscription authentication — PASS (AC16 MET)

- Started from **Connectors → OpenAI** in the Paperclip UI. The official **OpenAI Subscription** option was selected; the API-key path was not used.
- The owner performed the human authorization in the visible browser: Paperclip sign-in and the official OpenAI consent. No password, token, cookie or auth-file content was shared with, read by, or printed by the executor.
- The OpenAI account initially rejected the flow because device-code sign-in was disabled. The owner enabled it in ChatGPT Security Settings and repeated the consent. Paperclip then reported “Codex CLI is signed in. Click Connect to use this account.”
- After **Connect**, Paperclip saved the connection:
  - UI: `Kayzen’s OpenAI` (connection id `1ad1e9ca-6dde-40a7-9e18-90d6baf3bcb7`), status **Connected**, sign-in method **ChatGPT subscription**, access **Company shared**.
  - A live **Check usage** call succeeded and returned Codex quota data (Primary 5h at 1%, Secondary weekly at 81%, workspace spend control not reported). This proves the credential is accepted by OpenAI, not merely stored.
  - Read-only DB (no token values printed): `tool_connections` has one `OpenAI` row with `status=active`, `enabled=true`, `health_status=ok`, `auth_kind=oauth`, `credential_source=paperclip_vault`, `ownership=customer`, `connection_kind=managed`, `connection_purpose=ai`, `config.aiIsolatedSubscription=true`; its `connection_grants` row is `active` and not revoked.
  - `adapter_auth_sessions`: one row `status=authenticated` with non-null `connection_id` and `connection_grant_id`; descriptor `provider=openai`, `method=subscription`, `ownership=shared`, `allAgents=true`, `connection_method=local_subscription`. Four older rows remain `cancelled` from the failed attempts and are historical.
  - `ai_subscription_connections` remains empty in this build; the AI subscription connector is persisted in `tool_connections` (`connection_purpose=ai`, `connection_kind=managed`) with the vault credential and active grant described above. The UI usage check is the functional proof.
- The credential is managed in the **Paperclip vault**, not the CLI default profile. `codex login status` inside the container still reports “Not logged in”; per the Work Order, the CLI default is not the source of truth for the Paperclip adapter. The Paperclip UI plus the managed connection/grant above are authoritative. The UI quota figures are executor-recorded Paperclip observations; the managed connection, grant and authenticated session were independently corroborated by read-only DB queries.
- AC16: **MET**. No agent task ran, no API key was created, and no personal credential was copied.

## 4. Corrections applied

1. **Restore isolation (HIGH):** `Restore-Paperclip.ps1` now requires a new direct-child `restore-test-*` target, rejects existing targets, external/ancestor paths and reparse-point ancestors, and rejects `-Force`. The guard runs before extraction. `Expand-PaperclipBackupArchive` also rejects `-Force`, requires a SHA-256 sidecar and verifies it before extraction.
2. **Hidden files and backup coverage:** backups use .NET `ZipFile` with `Get-ChildItem -Force -Recurse`, so hidden files and nested hidden directories are included. Ephemeral `.codex/tmp` sandbox helpers are excluded. The SHA-256 sidecar is mandatory.
3. **Restored permissions:** a one-off pinned-image container repairs Linux ownership/mode (`0700`) on the restored data before it is used; the restored copy is never started with real credentials during isolation tests.
4. **Container identity:** health/startup/status verify the Compose project, exact pinned image and healthy state, preventing false positives from an unrelated HTTP 200 on port 3100.
5. **SonarCloud:** all 10 reported findings were fixed individually in `collect_windows_inventory.ps1` (6 empty catches now assign explicit `NOT_AVAILABLE`/`UNKNOWN`) and `collect_vps_inventory.sh` (positional parameter, `[[` tests, `NOT_AVAILABLE` constant). No issue was excluded or marked false-positive.
6. **ECC evidence:** `evidence/NLE-INFRA-WO-001-CD03-SECURITY-EVIDENCE.md` provides focused security evidence for the flagged surface; no permissions were expanded.
7. **Docker eligibility/cost:** the owner attests the organization is a small business under 250 employees and under US$10 million annual revenue, eligible for Docker Desktop’s free plan. `docker desktop auth status` shows personal plan, no organizations and no paid subscription; no paid runner/API/service was used. Additional spend: **US$0**.
8. **Operational docs and Work Order:** updated to state claim PASS, Codex auth PASS, AC16 MET, and the no-agent-execution boundary.

## 5. Tests

| Test | Result |
|---|---|
| `python scripts/validate_sources.py` | 7/7 groups PASS (364 sources, 6 ZIPs, 105 agents, 62 workflows, 40 WOs) |
| `python -m unittest discover -s tests -v` | **34/34 OK** |
| `Test-PaperclipDeployment.ps1` (offline) | **43/43 PASS**, 0 FAIL |
| `docker compose ... config --quiet` (base + local) | exit 0 |
| `bash -n scripts/infra/collect_vps_inventory.sh` | PASS |
| PowerShell parser, all `scripts/windows/*.ps1` | 0 errors |
| `python scripts/security/scan_repository.py` | 439 tracked files, **0 findings** |
| Git diff check | clean (no whitespace errors) |

The PowerShell suite covers existing targets, active directories, external paths, `-Force`, missing/tampered sidecars, hidden files, nested hidden directories and a real Windows junction (`RESTORE_ROOT_REPARSE_POINT`), plus live-data immutability (`live_sentinel_unchanged`). Static assertions are not presented as runtime proof; the runtime backup/restore was executed separately.

The auth gate changed documentation only; the immutable Python/PowerShell suites were not rerun unnecessarily. Final CI at the auth-gate HEAD is the authority. Authentication validation used the Paperclip UI and read-only database queries and did not execute an agent.

## 6. Backup and database consistency

- Pre-auth cold backup: `paperclip-data-20261126T185859Z-42fb1281.zip`, SHA-256 `933a478e8d5660da2e4ddfc677eb67680253c2eb37f45e94c913fb55a0d8cb00`, 4,723 entries.
- The archive includes hidden ownership markers, `instances/default/ai-local-logins/`, `instances/default/secrets/master.key`, `decision-signing.key`, `PG_VERSION` and `postgresql.conf`. It may contain account/session state and is therefore kept in the protected backup directory with owner-only ACL, outside Git.
- PostgreSQL was stopped gracefully for the cold copy; the internal `pnpm db:backup` reports `ok`. An isolated restore verified SHA-256, file count/size and required files with permissions repaired, and was **not started**. No restored instance ran with real credentials.
- The new subscription connection was created **after** this archive; the archive does not contain the new Paperclip-vault credential. A fresh cold backup must be taken before relying on restore for the authenticated state.
- Pre-claim isolated restore was started on a separate port and returned health 200; that result is retained as historical runtime evidence, not as proof of the Codex-authenticated state.

## 7. SonarCloud and ECC

- The public SonarCloud API initially returned 10 open issues for PR #3. Each has a code-level fix in this candidate. At correction commit `0fca04a`, the API returned **total=0**, the quality gate was **OK**, and the `SonarCloud Code Analysis` check passed. At `d77b4e4`/`41a3135`, SonarCloud reported one new `python:S6353` issue in the newly added scanner; it was fixed individually with `\w` character classes. At final code head `f1b0db6`, the API returns **total=0**, the quality gate is **OK**, and the check passes. No issue was excluded or marked false-positive.
- ECC Tools raised a predictive `action_required` alert on `deploy/local/agents/README.md`. The deterministic security regression gate (`scripts/security/scan_repository.py` plus CI step) was accepted: at `d77b4e4` and again at `f1b0db6` the ECC Security Evidence gate reports **success** — “No security-sensitive scanner-evidence gap detected”, 42 changed files scanned. The scanner checks tracked text for private keys, provider tokens, credential-bearing URLs and committed Paperclip secrets, rejects tracked runtime/secret paths, prints no matched values and uses only the existing `contents: read` permission. Check publication remains unavailable because the ECC app lacks Checks: write; no permission was expanded.

## 8. Context Lock

- All SHA-256 fingerprints for the canonical file set were recalculated from the corrected working tree and recorded in `locks/NLE-INFRA-WO-001-context-lock.json`.
- Historical CD-02 SHA-256 values and Git blob identities are retained for provenance; they are not presented as current.
- The lock cannot contain its own final commit hash; final HEAD and CI are verified externally after push.

## 9. Residual risks

1. `Zeus` remains paused; no agent task ran. Any activation requires separate authorization and a new preflight.
2. The existing cold backup predates the subscription connection; take a fresh cold backup before relying on restore for the authenticated state.
3. Backups contain claim/session state and secret keys; they must remain private and never be committed or shared.
4. Docker Desktop eligibility relies on the owner’s small-business attestation; no paid plan was purchased.
5. C: free space is low (~9.9 GiB at last check); monitor Docker growth.
6. Final CI and an independent read-only audit of the auth-gate HEAD are required before merge.

## 10. Verdict

**APPROVED — AUTH GATE MET; FINAL CI AND INDEPENDENT AUDIT PASSED.**

The local runtime, claim, Codex subscription connection and AC16 are satisfied: Paperclip reports the OpenAI connection as Connected/ChatGPT subscription, the live usage check succeeded, and the managed vault connection/grant are active. Restore isolation, hidden-file backup coverage, container identity, SonarCloud and ECC gates remain valid. `Zeus` stayed paused, no agent task ran, no API key was created and no credential was copied. Auth-gate head `51dbfeb` passed CI run `45892550947`, SonarCloud reports 0 open issues/gate OK, and the ECC gate passed; a documentation-only follow-up commit carries this verdict. No merge, checkpoint promotion, sprint start, VPS access or additional spend is authorized by this record.

## 11. Independent read-only audit

- An independent read-only agent audited auth-gate head `51dbfeb` and the runtime evidence: verdict **APPROVED**, no HIGH/CRITICAL findings.
- It independently verified the managed connection in the database: one `tool_connections` OpenAI row active/enabled/health ok with `credential_source=paperclip_vault` and `config.aiIsolatedSubscription=true`; one active, non-revoked organization grant; one `authenticated` adapter session with non-null connection/grant; older cancelled sessions historical; `ai_subscription_connections` empty as documented.
- It confirmed `Zeus` paused, zero agent task/run rows, health/identity/loopback unchanged, Docker small-business attestation accurately labeled, all 44 SHA-256 and 44 Git-blob fingerprints matching, CI/Sonar/ECC passing, and **AC16 MET** not merely owner-confirmed.
- Its LOW finding (lock still said 437 scanned files instead of 439) was corrected in this commit; its INFO notes were addressed by clarifying `config.aiIsolatedSubscription` and labeling the quota figures as UI observations. No code changed after the audited head.
