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
- Codex subscription auth: **PASS / AC16 MET**.
  - Official flow: Connectors → OpenAI → **OpenAI Subscription**; no API key. The owner completed the Paperclip sign-in and OpenAI consent in the visible browser. No password, token, cookie or auth-file content was read or printed by the executor.
  - OpenAI initially rejected the device flow because device-code sign-in was disabled; the owner enabled it in ChatGPT Security Settings and repeated consent.
  - Paperclip UI: connection `Kayzen’s OpenAI` (id `1ad1e9ca-6dde-40a7-9e18-90d6baf3bcb7`), **Connected**, sign-in method **ChatGPT subscription**, access **Company shared**. A live **Check usage** call succeeded with Codex quota data (Primary 1%, Secondary weekly 81%).
  - Read-only DB, no secret values: `tool_connections` has one `OpenAI` row with `status=active`, `enabled=true`, `health_status=ok`, `auth_kind=oauth`, `credential_source=paperclip_vault`, `ownership=customer`, `connection_kind=managed`, `connection_purpose=ai`, `aiIsolatedSubscription=true`; its `connection_grants` row is `active` and not revoked.
  - `adapter_auth_sessions`: one `status=authenticated` row with non-null `connection_id` and `connection_grant_id`; descriptor `provider=openai`, `method=subscription`, `ownership=shared`, `allAgents=true`, `connection_method=local_subscription`. Four older `cancelled` rows are historical failed attempts.
  - `ai_subscription_connections` is empty in this build; the AI subscription connector is stored in `tool_connections` (`connection_purpose=ai`, `connection_kind=managed`) with `credential_source=paperclip_vault` and an active grant. The live usage check is the functional proof.
  - The credential is in the **Paperclip vault**, not the CLI default profile. `codex login status` still reports “Not logged in”; this is not the Paperclip adapter’s source of truth. The managed connection/grant and successful usage check are authoritative.
  - One default agent row exists (`Zeus`, `codex_local`, `status=paused`, created 18:34:46 UTC) as a claim/bootstrap side effect. It has not run; no agent-task/run table contains rows.
  - No tokens, cookies or auth-file contents were read or printed. No API key was created.

## 3. Secrets

- `BETTER_AUTH_SECRET` and `PAPERCLIP_TOOL_ACTION_SIGNING_SECRET` are stored outside Git at `D:\NexLabs\Paperclip\secrets\paperclip.env`.
- File: 2 lines, 186 bytes; ACL protected (`AreAccessRulesProtected=True`, one owner ACE); values were never printed, logged or committed.
- Container secret keys `instances/default/secrets/master.key` and `decision-signing.key` are included in protected backups and have owner-only ACL on the backup.
- Secret scan of versioned files: 0 private keys, tokens, credentials in URLs or 64-hex secret values. The committed CI scanner covers these categories; it does not include e-mail/CPF/CNPJ rules.

## 4. Backup and restore security

- Pre-auth cold backup: `paperclip-data-20261126T185859Z-42fb1281.zip`, SHA-256 `933a478e8d5660da2e4ddfc677eb67680253c2eb37f45e94c913fb55a0d8cb00`.
- 4.723 entries; includes hidden `.paperclip-ownership-verified`, `instances/default/ai-local-logins/`, `instances/default/secrets/master.key`, `instances/default/secrets/decision-signing.key`, `instances/default/db/PG_VERSION` and `postgresql.conf`.
- The new subscription connection was created after this archive; the archive does not contain the new Paperclip-vault credential. A fresh cold backup is required before relying on restore for the authenticated state.
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
- Owner attestation: the organization is a **small business with fewer than 250 employees and under US$10 million annual revenue**, eligible for Docker Desktop’s free plan. No paid plan was purchased.
- Additional spend: **US$0**. No CI paid runner, cloud provider or paid service was used.

## 8. Residual risks

1. `Zeus` remains paused and no agent task ran; activation requires separate authorization.
2. The pre-auth cold backup does not contain the new subscription credential; take a fresh cold backup before relying on restore for the authenticated state.
3. Backups contain claim/DB state and secret keys; they must remain in the protected directory and never be committed or shared.
4. Final CI and independent read-only audit of the auth-gate HEAD remain required before merge.
5. C: free space is ~9.9 GiB; Docker data ~17 GiB. Monitor capacity.
