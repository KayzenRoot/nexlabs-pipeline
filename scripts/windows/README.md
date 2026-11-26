# Windows Paperclip operations

All scripts are non-interactive, use the pinned image/digest and never print
secret values.

| Script | Purpose |
|---|---|
| `Initialize-PaperclipSecrets.ps1` | Create protected local data/secrets/backups directories and generate `BETTER_AUTH_SECRET` and `PAPERCLIP_TOOL_ACTION_SIGNING_SECRET` once. |
| `Start-Paperclip.ps1` | Require Docker Desktop/WSL2, verify secrets/port, start the pinned compose stack and wait for `/api/health`. |
| `Stop-Paperclip.ps1` | Graceful `docker compose stop`; preserves data and volumes. |
| `Get-PaperclipStatus.ps1` | Show compose status and health without printing secrets. |
| `Backup-Paperclip.ps1` | Stop safely, archive the full Paperclip data directory, write SHA-256 sidecar, restart. |
| `Restore-Paperclip.ps1` | Verify the sidecar and restore into an isolated target; never replaces live data automatically. |
| `Test-PaperclipDeployment.ps1` | Offline static/integrity/backup/restore/secret/port self-test; optional compose config check when Docker is available. |

## Defaults

- Root: `D:\NexLabs\Paperclip` when D: exists, otherwise `%LOCALAPPDATA%\NexLabs\Paperclip`.
- Data: `<root>\data`.
- Secrets: `<root>\secrets\paperclip.env`, owner-only ACL.
- Backups: `<root>\backups`.
- Port: `3100`, bound to `127.0.0.1` only.

Override the root with `-Root` or `NEXLABS_PAPERCLIP_ROOT`.

## Safety

- If Docker Desktop/WSL2 is absent, the scripts fail closed and do not install,
  enable Windows features, reboot or start a paid service.
- No `docker compose down -v`, volume removal, prune or force-recreate.
- No API keys, no Codex auth file copying, no agent/workflow activation.
