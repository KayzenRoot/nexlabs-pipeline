# Local-first Paperclip (Windows 11)

This override is for the owner's Windows 11 host with Docker Desktop/WSL2.
It publishes Paperclip only on `127.0.0.1:3100` and bind-mounts the persistent
data directory.

## Docker Desktop prerequisite

Docker Desktop and the `docker` CLI must be installed and running with the WSL2
backend. If they are absent, this Work Order does **not** install Docker Desktop,
enable Windows features or reboot the host. The runtime is BLOCKED until the
owner authorizes that administrative action.

## Commands

```powershell
# 1. Generate the two local secrets once; protected directory outside Git.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Initialize-PaperclipSecrets.ps1

# 2. Start the pinned image and wait for http://127.0.0.1:3100/api/health.
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Start-Paperclip.ps1

# 3. Status; 4. safe stop (no volumes removed).
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Get-PaperclipStatus.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/windows/Stop-Paperclip.ps1
```

## Files

- `compose.yaml` — loopback port and data bind mount.
- `.env.example` — non-secret local values only.
- `codex/` — official Codex integration notes; no auth files.
- `agents/` — catalog preservation notes; no agents imported.

## Safety

- Never change the port binding to `0.0.0.0` or a LAN address.
- Never commit the protected `paperclip.env`.
- Never use `docker compose down -v`.
- Stop gracefully and keep the data mount for persistence.
