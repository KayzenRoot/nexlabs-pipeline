"""Workflow-specific authorization wrapper using the approved security contracts."""
from __future__ import annotations

from datetime import datetime

from security.approval import SignatureVerifier
from security.authorization import authorize
from security.contracts import (
    AccessDecision, AccessRequest, ApprovalEnvelope, Grant, require,
)

from .ledger import Ledger


class _LedgerNonceStore:
    """Private adapter; nonce consumption stays behind the ledger primitive."""

    def __init__(self, ledger: Ledger):
        self.ledger = ledger

    def consume(self, nonce: str, expires_at: datetime, now: datetime) -> bool:
        return self.ledger._consume(nonce, expires_at, now)


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
    nonce_store=None,
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
        nonce_store=nonce_store or _LedgerNonceStore(ledger),
    )
