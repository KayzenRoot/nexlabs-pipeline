# Offline security control contracts | NLE-INFRA-WO-002/CD-01

This package is a real local policy evaluator and set of validators, but it is **not connected to Paperclip, a network, a secret store or a host**.

## Verify

```sh
python -m security verify
python -m unittest discover -s tests -v
```

## Implemented contracts

- Exact identity/grant intersection across principal, action, target, tenant, project, task, workflow, skill, host, provider, risk, policy hash and policy epoch. The caller supplies the trusted current policy hash/epoch; principal claims must come from a trusted identity adapter, not raw user input. No hierarchy inheritance or privileged bypass.
- Default deny; only internal-only requests with zero spend can be authorized.
- HIGH_ASSURANCE approval envelope binds actor, independent human approver, action, target, tenant, payload/policy hashes, evidence, zero-cost ceiling, expiry and a one-time nonce.
- Signature verifier is pluggable. The included HMAC-SHA256 adapter is test-only. Production signer/key custody remains unselected and must be approved separately.
- Nonce storage is an interface; the included in-memory implementation is test-only and not crash-safe. Durable event/approval ledger belongs to NLE-WF-WO-001.
- Generic private network descriptors reject public/wildcard/default routes. No WireGuard choice or config is generated because INFRA-ADR-003 remains PROPOSED.
- SecretRef is metadata only. No secret values are read, written, generated, rotated or resolved.
- Workspace paths are confined to tenant/project/task roots; symlink and Windows reparse components are rejected. This is a preflight guard, not a race-free OS sandbox.

## Explicit non-capabilities

No sockets, subprocesses, environment credential reads, Paperclip API/DB, VPS/SSH, firewall, DNS, WireGuard, Docker, host mounts, secret provider, production signature keys, agent execution, workflow dispatch or external effects. No dependencies beyond Python standard library. No generated policy grants.

## Production gates still open

Ratify the network transport ADR; implement and independently qualify the chosen private transport; bind real human identities and service principals; select protected OS secret/signature custody; implement durable nonce/approval ledger; validate live Paperclip API contracts; prove cross-tenant isolation; run host/network tests; obtain explicit approval before any runtime or VPS action.
