"""Workflow-specific authorization wrapper using the approved security contracts."""
from __future__ import annotations

from security.approval import SignatureVerifier
from security.authorization import authorize
from security.contracts import (
    AccessDecision, AccessRequest, ApprovalEnvelope, Grant, require,
)

from .ledger import Ledger


def authorize_workflow(
    ledger: Ledger,
    request: AccessRequest,
    grants: list[Grant],
    *,
    current_policy_sha256: str,
    current_policy_epoch: int,
    approval: ApprovalEnvelope | None = None,
    approval_signature: str | None = None,
    verifier: SignatureVerifier | None = None,
) -> AccessDecision:
    """Authorize one workflow action with the durable ledger as nonce store."""
    require(request.action.startswith("workflow."), "WORKFLOW_ACTION_REQUIRED")
    return authorize(
        request, grants,
        current_policy_sha256=current_policy_sha256,
        current_policy_epoch=current_policy_epoch,
        approval=approval,
        approval_signature=approval_signature,
        verifier=verifier,
        nonce_store=ledger,
    )
