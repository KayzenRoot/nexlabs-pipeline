# Future VPS composition (Oracle Ubuntu ARM64)

**Do not execute this from the Windows local-first host.** This directory prepares
the future private VPS deployment; it does not authorize SSH, firewall/NSG/DNS
changes, remote secret creation, deploy or migration.

## Design

- Same pinned Paperclip image/index digest as local, including `linux/arm64`.
- External `postgres:17-alpine` pinned by immutable index digest.
- `DATABASE_URL` supplied from an independent VPS secret file, never Git.
- Paperclip port published only on `127.0.0.1:3100`; private access is expected
  through the future WireGuard/reverse-proxy design, never the public IP.
- Separate persistent bind mounts for Paperclip data and PostgreSQL data.
- Database healthcheck and `depends_on` before Paperclip starts.
- Independent secrets from the local environment; no secret reuse.

## Future execution gates

1. Owner authorization and read-back of the VPS inventory.
2. WireGuard/private access qualified and firewall/NSG changes separately approved.
3. Independent VPS secrets created outside Git.
4. Logical migration plan from local embedded PostgreSQL to external PostgreSQL.
5. Backup/restore rehearsal on the target before any production use.

No command in this directory is part of NLE-INFRA-WO-001/CD-02 execution.
