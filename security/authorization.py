"""Exact-scope, default-deny authorization evaluator."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .approval import NonceStore, SignatureVerifier, verify_approval
from .contracts import (
    AccessDecision, AccessRequest, ApprovalEnvelope, Grant, SecurityError,
    as_decimal, require, require_hash, require_id, require_utc, RISKS, KINDS,
)


def _deny(reason: str) -> AccessDecision:
    return AccessDecision(False, reason)


def _valid_grant(grant: Grant, request: AccessRequest) -> bool:
    dimensions = (
        (grant.principal_id, request.actor.principal_id),
        (grant.action, request.action),
        (grant.target_id, request.target_id),
        (grant.tenant_id, request.tenant_id),
        (grant.project_id, request.project_id),
        (grant.task_id, request.task_id),
        (grant.workflow_id, request.workflow_id),
        (grant.skill_id, request.skill_id),
        (grant.host_id, request.host_id),
        (grant.provider_id, request.provider_id),
        (grant.risk, request.risk),
        (grant.policy_sha256, request.policy_sha256),
        (grant.policy_epoch, request.policy_epoch),
    )
    return all(actual == expected for actual, expected in dimensions)


def authorize(
    request: AccessRequest,
    grants: Iterable[Grant],
    *,
    approval: ApprovalEnvelope | None = None,
    approval_signature: str | None = None,
    verifier: SignatureVerifier | None = None,
    nonce_store: NonceStore | None = None,
) -> AccessDecision:
    """Evaluate one internal-only request. Unknown or missing evidence always denies."""
    try:
        require_utc(request.now)
        actor = request.actor
        require(actor.kind in KINDS and actor.state == "ACTIVE", "PRINCIPAL_NOT_ACTIVE")
        for value in (
            actor.principal_id, actor.tenant_id, actor.project_id, actor.host_id,
            request.action, request.target_id, request.tenant_id, request.project_id,
            request.task_id, request.workflow_id, request.skill_id, request.host_id,
            request.provider_id,
        ):
            require_id(value, "REQUEST_SCOPE_INVALID")
        require(request.risk in RISKS, "RISK_UNKNOWN")
        require_hash(request.policy_sha256)
        require_hash(request.payload_sha256)
        require(isinstance(request.policy_epoch, int) and request.policy_epoch > 0,
                "POLICY_EPOCH_INVALID")
        require(actor.policy_epoch == request.policy_epoch, "PRINCIPAL_POLICY_STALE")
        require(actor.tenant_id == request.tenant_id, "TENANT_ISOLATION_DENY")
        require(actor.project_id == request.project_id, "PROJECT_ISOLATION_DENY")
        require(actor.host_id == request.host_id, "HOST_BINDING_DENY")
        require(request.effect == "INTERNAL_ONLY", "EXTERNAL_EFFECTS_DENY")
        require(as_decimal(request.requested_spend_usd) == 0, "SPEND_FORBIDDEN")
        require(not request.action.startswith(("grant.", "policy.", "identity.", "secret.export")),
                "PRIVILEGE_MUTATION_DENY")

        selected = None
        for grant in grants:
            if not isinstance(grant, Grant):
                continue
            try:
                require(not grant.revoked, "GRANT_REVOKED")
                require_utc(grant.issued_at)
                require_utc(grant.expires_at)
                require(grant.issued_at <= request.now < grant.expires_at, "GRANT_EXPIRED")
                require(as_decimal(grant.max_spend_usd) == 0, "GRANT_SPEND_FORBIDDEN")
                require(grant.external_effects == "DENY", "GRANT_EXTERNAL_EFFECTS")
                if _valid_grant(grant, request):
                    selected = grant
                    break
            except SecurityError:
                continue
        require(selected is not None, "NO_EXACT_SCOPE_GRANT")

        if request.risk == "HIGH_ASSURANCE":
            require(approval is not None and approval_signature is not None
                    and verifier is not None and nonce_store is not None,
                    "INDEPENDENT_HUMAN_APPROVAL_REQUIRED")
            verify_approval(approval, approval_signature, verifier, nonce_store, request)

        return AccessDecision(True, "AUTHORIZED_INTERNAL_ONLY", selected.grant_id)
    except (SecurityError, AttributeError, TypeError) as exc:
        reason = str(exc) if isinstance(exc, SecurityError) else "INVALID_REQUEST"
        return _deny(reason)
