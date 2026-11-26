# NexLabs Paperclip deployment (LOCAL FIRST)

This directory is the portable deployment contract for **NLE-INFRA-WO-001/CD-02**.
The first target is a local Paperclip instance on Windows 11. The VPS Oracle
Ubuntu ARM64 composition is prepared here but **must not be executed** in this
Work Order.

## Current scope

- Paperclip official self-hosted image, pinned by immutable OCI index digest.
- Docker Desktop with WSL2 backend and Linux containers.
- Embedded PostgreSQL in the local quickstart, persisted under the data mount.
- UI/API only at `http://localhost:3100`, bound to `127.0.0.1`.
- Two independent local secrets, `BETTER_AUTH_SECRET` and
  `PAPERCLIP_TOOL_ACTION_SIGNING_SECRET`, stored outside Git in a protected
  directory and never printed or committed.
- No Cloud image, no API keys, no agent execution, no heartbeats, routines,
  workflows, external effects, subscriptions or spend.
- No VPS access, SSH, firewall/NSG/DNS change, deploy or remote secret.

## Image lock

`deploy/image-lock.json` is the authoritative pin:

- Paperclip `2026.1117.0`, index
  `sha256:bdf38d10544dc6c831e16dc027f23ad586353ef3be1a1b2c6979e63b956aceb1`,
  with verified `linux/amd64` and `linux/arm64` manifests.
- PostgreSQL `17-alpine`, index
  `sha256:f9cf3e1f0066f0eb0c48707d864f0ac5941e9ff454a072077d97a4d278d07d73`,
  used only by the future VPS external-database composition.

Do not replace either digest with `latest` or a mutable tag.

## Prerequisites

1. Windows 11 with virtualization enabled.
2. Docker Desktop installed and running with the WSL2 backend.
3. At least 8 GiB RAM available for Docker; this host has more.
4. A persistent data location with free space for the embedded database,
   uploads and agent workspaces.
5. TCP port `3100` free on loopback.

If Docker Desktop or WSL2 is unavailable, do not enable Windows features,
install privileged components or reboot without owner authorization. The
runtime remains BLOCKED and the exact administrative action must be reported.

## Windows quickstart

Run from the repository root in PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Initialize-PaperclipSecrets.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Start-Paperclip.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Get-PaperclipStatus.ps1
```

Open `http://localhost:3100` and claim the instance in the browser. Do not
create agents, heartbeats, routines, workflows or external effects.

Safe stop (preserves data and volumes):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Stop-Paperclip.ps1
```

Never use `docker compose down -v`; it removes volumes and data.

## Local paths

The scripts default to `D:\NexLabs\Paperclip` when the D: drive exists, otherwise
`%LOCALAPPDATA%\NexLabs\Paperclip`. Override with `-Root` or
`NEXLABS_PAPERCLIP_ROOT`.

- `data\` — Paperclip home, embedded PostgreSQL, assets, workspaces (Git-ignored).
- `secrets\paperclip.env` — two local secrets, owner-only ACL (Git-ignored).
- `backups\` — protected full-data backups and SHA-256 sidecars (Git-ignored).
- `restore-test-*\` — isolated restore targets (Git-ignored).

## Backup and restore

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Backup-Paperclip.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Restore-Paperclip.ps1 `
  -BackupPath D:\NexLabs\Paperclip\backups\paperclip-data-YYYYMMDDTHHMMSSZ.zip `
  -TargetDataDir D:\NexLabs\Paperclip\restore-test-YYYYMMDD
```

The backup script stops Paperclip gracefully, archives the complete data
directory, writes a SHA-256 sidecar, then starts Paperclip again. The restore
script verifies the sidecar and expands into an **isolated** target. It does not
replace live data automatically; switching live data is a manual, reviewed
operation after validation.

## Codex preparation

Paperclip's official image includes the Codex CLI and the `codex_local` adapter.
Use subscription authentication through the Paperclip UI/browser when the owner
authorizes it. Do not set `OPENAI_API_KEY`, do not copy personal Codex auth
files, and do not run agent tasks during installation. See
`deploy/local/codex/README.md`.

## NexLabs catalog

The 105 agents, 10 departments, 92 packages, 1,110 assignments, 1,071 contextual
competencies, 62 workflows and 35 surfaces remain in the immutable Source Pack.
Nothing is imported, hired or activated here. See `deploy/local/agents/README.md`.

## Future VPS

`deploy/vps/compose.yaml` prepares the Oracle Ubuntu ARM64 target with an
external PostgreSQL 17, independent secrets, persistence and private access. It
is not executed in this Work Order. See `deploy/vps/README.md`.
