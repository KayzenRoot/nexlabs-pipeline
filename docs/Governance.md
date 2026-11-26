# Governance

ANALYZE → SOURCE CHECK → NEXT NECESSARY INCREMENT → WORK ORDER → CONTEXT LOCK → PREFLIGHT → EXECUTOR → TESTS/EVIDENCE → PR → AUDIT → APPROVED / CORRECTION REQUIRED / BLOCKED → CHECKPOINT DELTA → MERGE → NEXT.

One active WO. Same ID in branch, PR, evidence and corrections. No force-push, bypass, history rewrite or self-approval. No advancement with HIGH/CRITICAL findings. Executor must inspect, test, commit, push and report in pt-BR; independent reviewer promotes checkpoint only after evidence. Require main protection, PR-only, squash-only, no force-push/delete, actual required checks, minimal permissions, pinned action SHAs, no secrets in PR. Verify availability, quota and billing before any CI run. No new subscription or paid reviewer. If unavailable, BLOCKED, not simulated enforcement. No automatic configuration changes without verification.

Public repository exception NLE-ADR-BOOT-007: only reviewed non-sensitive planning/development; no secrets or real customer data. No production exposure. The initial main commit was a minimal README required to establish a PR base. Existing branch chore/nle-bootstrap-001 is the sole branch for this WO; no duplicate branch required.
