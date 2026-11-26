# NLE-INFRA-WO-001/CD-03 — Security Evidence

Scope: local Paperclip runtime, protected credentials, backup/restore isolation, container identity, SonarCloud fixes and ECC security-evidence response. No VPS, agents, workflows, API keys, deploy or spend.

## 1. Runtime identity and exposure

- Container: `nexlabs-paperclip-paperclip-1`; Compose project `nexlabs-paperclip`; status **healthy**.
- Image: `ghcr.io/paperclipai/paperclip:2026.1117.0@sha256:bdf38d10544dc6c831e16dc027f23ad586353ef3be1a1b2c6979e63b956aceb1` (matches image lock).
- Port: `127.0.0.1:3100->3100/tcp`; `Get-NetTCPConnection -LocalPort 3100 -State Listen` returns only `127.0.0.1`.
- Health: HTTP 200; `status=ok`, `deploymentMode=authenticated`, `deploymentExposure=private`, `bootstrapStatus=ready`, `databaseBackup.status=ok`.
- Startup/health now requires the exact Compose container and pinned image; an unrelated HTTP 200 is rejected (`PAPERCLIP_CONTAINER_NOT_FOUND`, `PAPERCLIP_IMAGE_MISMATCH`, `PAPERCLIP_CONTAINER_NOT_HEALTHY`, `PORT_IN_USE_UNRELATED_SERVICE`).

## 2. Claim and Codex authentication

- Claim: **PASS** — health reports `bootstrapStatus=ready` (pre-claim was `bootstrap_pending`).
- Codex subscription auth: **FAIL**.
  - `codex login status` inside the container returns **“Not logged in”** both for default home and `CODEX_HOME=/paperclip/.codex`.
  - Read-only DB audit: `adapter_auth_sessions` has 3 `codex_local` sessions, all `status=cancelled` (created/updated 18:34:53–18:38:46 UTC); `result_claim`, `connection_id` and `grant_id` are null; `ai_subscription_connections` has 0 rows; `ai_connection_pools` 0; `ai_provider_defaults` 0; `tool_connections` 0.
  - One default agent row exists (`Zeus`, `codex_local`, `status=paused`, created 18:34:46 UTC) as a claim/bootstrap side effect. It has not run; no agent-task/run table contains rows. Its `adapter_config` contains only non-auth sandbox settings.
  - No Codex auth files were found under `/home/node/.codex` or `/paperclip/.codex` (only ephemeral `tmp/arg0-linux` helper directories).
  - No tokens, cookies or auth-file contents were read or printed.
- Consequence: no agent tasks were executed; AC16 is unmet and Codex-dependent execution remains blocked until the owner completes a successful login in the container/Paperclip adapter. Owner confirmation alone is not treated as proof.

## 3. Secrets

- `BETTER_AUTH_SECRET` and `PAPERCLIP_TOOL_ACTION_SIGNING_SECRET` are stored outside Git at `D:\NexLabs\Paperclip\secrets\paperclip.env`.
- File: 2 lines, 186 bytes; ACL protected (`AreAccessRulesProtected=True`, one owner ACE); values were never printed, logged or committed.
- Container secret keys `instances/default/secrets/master.key` and `decision-signing.key` are included in protected backups and have owner-only ACL on the backup.
- Secret scan of versioned files: 0 private keys, tokens, credentials in URLs or 64-hex secret values. The committed CI scanner covers these categories; it does not include e-mail/CPF/CNPJ rules.

## 4. Backup and restore security

- Post-claim backup: `paperclip-data-20261126T185859Z-42fb1281.zip`, SHA-256 `933a478e8d5660da2e4ddfc677eb67680253c2eb37f45e94c913fb55a0d8cb00`.
- 4.723 entries; includes hidden `.paperclip-ownership-verified`, `instances/default/ai-local-logins/`, `instances/default/secrets/master.key`, `instances/default/secrets/decision-signing.key`, `instances/default/db/PG_VERSION` and `postgresql.conf`.
- `.codex/tmp` ephemeral root-owned sandbox helpers are excluded; auth/config/DB/secrets remain included.
- Backup directory and archive ACL: owner-only, inheritance protected.
- Cold backup: container is gracefully stopped before archiving and restarted after; DB files are copied in a stopped state.
- Isolated restore: `Restore-Paperclip.ps1` verified SHA-256, created a new direct-child `restore-test-*` target, repaired Linux permissions (`0700`) with the pinned image, and verified 4.443 files/106,9 MB, `master.key`, `PG_VERSION`, `ai-local-logins`, hidden ownership marker and owner-only ACL.
- The restored copy was **not started** and was deleted after verification; no restored instance ran with real credentials.
- Restore isolation tests: 43/43 PASS, including existing targets, active directories, external paths, direct-child rule, `-Force` rejection, sidecar requirement, tamper detection, hidden files and a real Windows junction (`RESTORE_ROOT_REPARSE_POINT`).

## 5. SonarCloud — reported issues resolved individually (10 original + 1 new scanner finding)

| Issue | Rule | Location | Resolution |
|---|---|---|---|
| `AaIYOWMF1e1fHYi43K1g` | powershelldre:S8657 | `collect_windows_inventory.ps1:32` | Empty catch now sets `$os = "NOT_AVAILABLE"` |
| `AaIYOWMF1e1fHYi43K1h` | S8657 | `:44` | Catch sets `$processors = @("NOT_AVAILABLE")` |
| `AaIYOWMF1e1fHYi43K1i` | S8657 | `:47` | Catch sets `$gpus = @("NOT_AVAILABLE")` |
| `AaIYOWMF1e1fHYi43K1j` | S8657 | `:57` | Catch sets `$volumes = @("NOT_AVAILABLE")` |
| `AaIYOWMF1e1fHYi43K1k` | S8657 | `:61` | Catch sets `$services = @("NOT_AVAILABLE")` |
| `AaIYOWMF1e1fHYi43K1l` | S8657 | `:89` | Catch sets `$codexLoginStatus = "UNKNOWN"` |
| `AaIYOWKr1e1fHYi43K1d` | shell:S7679 | `collect_vps_inventory.sh:11` | Positional parameter assigned to `local cmd="$1"` |
| `AaIYOWKr1e1fHYi43K1e` | shell:S7688 | `:17` | `[` replaced by `[[` |
| `AaIYOWKr1e1fHYi43K1f` | shell:S7688 | `:24` | `[` replaced by `[[` |
| `AaIYOWKr1e1fHYi43K1c` | shell:S1192 | `:114` | `NOT_AVAILABLE` constant defined and reused 8 times |
| `AaIZUJIeG8sBJogj31Sh` | python:S6353 | `scripts/security/scan_repository.py:23` | New scanner finding: concise `\w` character classes replace `[A-Za-z0-9_]` |

No issues were excluded or marked false-positive artificially. `bash -n scripts/infra/collect_vps_inventory.sh` passes; inventory scripts remain read-only. At correction commit `0fca04a`, the SonarCloud API reported **total=0** open issues for PR #3, the quality gate was **OK**, and the `SonarCloud Code Analysis` check passed. At `d77b4e4`/`41a3135`, SonarCloud reported one new `python:S6353` issue in the new scanner; it was fixed individually (`\w` character classes). At final code head `f1b0db6`, the API returns **total=0**, the gate is **OK**, and the check passes.

## 6. ECC security-evidence response

- ECC alert on `deploy/local/agents/README.md` is a predictive “security-sensitive surface without scanner evidence” signal, not a vulnerability proof.
- This file and the new regression tests provide focused security evidence: secret scan, ACL, container identity, loopback bind, restore isolation, hidden-file backup coverage, junction rejection and auth-status verification.
- The deterministic security regression gate was accepted at `d77b4e4` and again at `f1b0db6`: the ECC Security Evidence gate reports **success** (“No security-sensitive scanner-evidence gap detected”, 42 changed files scanned). `scripts/security/scan_repository.py` runs in CI with the existing `contents: read` permission, scans tracked text for private keys/provider tokens/credential URLs/committed Paperclip secrets, rejects tracked runtime paths and never prints matched values. Final run: 439 tracked files, 0 findings.
- No integration permissions were expanded. Check publication remains dependent on the ECC app owner enabling Checks: read/write; this Work Order did not change that.

## 7. Docker Desktop eligibility and cost

- Docker Desktop **4.100.1** installed from the official installer (SHA-256 `98b24fd6…39b2`); no larger runner, paid API or billing change was created by this execution.
- `docker desktop auth status` reports Plan `personal`, no organizations, `Must Log In=false` and `Business Enforced=false`; account identifiers were not recorded.
- Docker Desktop free eligibility depends on Docker’s subscription terms (personal, education, non-commercial open source, or small business under the published employee/revenue thresholds). The owner must attest the organization’s commercial size; no paid plan was purchased.
- Additional spend: **US$0**. No CI paid runner, cloud provider or paid service was used.

## 8. Residual risks

Independent read-only audit at `b7a20f4`: **APPROVED** for the CD-03 correction/evidence scope, no HIGH/CRITICAL findings; it independently confirmed the Codex blocker and AC16 NOT MET.

1. Codex subscription auth is not present in the container (3 cancelled sessions, no auth file, CLI reports Not logged in); owner must complete it before any agent execution.
2. Docker Desktop commercial licensing eligibility requires owner attestation.
3. Backups now contain claim/DB state and secret keys; they must remain in the protected directory and never be committed or shared.
4. Runtime audit remains pending independent review.
5. C: free space is ~9.9 GiB; Docker data ~17 GiB. Monitor capacity.
