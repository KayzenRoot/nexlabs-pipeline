"""Single authorized command boundary for the offline workflow ledger."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Callable

from security.approval import SignatureVerifier
from security.contracts import (
    AccessDecision, AccessRequest, ApprovalEnvelope, Grant, Principal, require,
)

from .authorization import authorize_workflow
from .contracts import WorkflowEvent
from .ledger import Ledger

SOURCE_LOCK_SHA256 = "a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e"
Authorizer = Callable[..., AccessDecision]


class WorkflowCommands:
    """The only public mutation boundary. Ledger primitives stay private."""

    def __init__(
        self,
        ledger: Ledger,
        *,
        actor: Principal,
        tenant_id: str,
        project_id: str,
        task_id: str,
        workflow_id: str,
        policy_sha256: str,
        policy_epoch: int,
        risk: str = "STANDARD",
        grants: tuple[Grant, ...] = (),
        approval: ApprovalEnvelope | None = None,
        approval_signature: str | None = None,
        verifier: SignatureVerifier | None = None,
        authorizer: Authorizer = authorize_workflow,
    ):
        self.ledger = ledger
        self.actor = actor
        self.tenant_id = tenant_id
        self.project_id = project_id
        self.task_id = task_id
        self.workflow_id = workflow_id
        self.policy_sha256 = policy_sha256
        self.policy_epoch = policy_epoch
        self.risk = risk
        self.grants = grants
        self.approval = approval
        self.approval_signature = approval_signature
        self.verifier = verifier
        self.authorizer = authorizer

    def _request(self, action: str, target_id: str, payload_sha256: str,
                 now: datetime) -> AccessRequest:
        return AccessRequest(
            actor=self.actor, action=action, target_id=target_id,
            tenant_id=self.tenant_id, project_id=self.project_id, task_id=self.task_id,
            workflow_id=self.workflow_id, skill_id="workflow-skill",
            host_id=self.actor.host_id, provider_id="provider-local", risk=self.risk,
            policy_sha256=self.policy_sha256, policy_epoch=self.policy_epoch,
            payload_sha256=payload_sha256, effect="INTERNAL_ONLY",
            requested_spend_usd=Decimal("0"), now=now,
        )

    def _execute(self, request: AccessRequest, apply: Callable[[], None]) -> AccessDecision:
        with self.ledger.transaction():
            decision = self.authorizer(
                self.ledger, request, self.grants,
                current_policy_sha256=self.policy_sha256,
                current_policy_epoch=self.policy_epoch,
                approval=self.approval,
                approval_signature=self.approval_signature,
                verifier=self.verifier,
            )
            require(decision.allowed and decision.grant_id is not None, "COMMAND_DENIED")
            apply()
            if self.approval is not None:
                self.ledger._record_approval(
                    self.approval.approval_id, request.target_id, request.tenant_id,
                    self.approval.approver_id, request.action, request.payload_sha256,
                    request.policy_sha256, self.approval.nonce,
                    self.approval.expires_at, decision.reason, request.now,
                )
            return decision

    def create_run(self, run_id: str, workflow_version: str, event: WorkflowEvent,
                   now: datetime, deadline_at: datetime) -> AccessDecision:
        require(event.tenant_id == self.tenant_id, "EVENT_TENANT_MISMATCH")
        request = self._request("workflow.run.create", run_id, event.digest(), now)
        return self._execute(
            request,
            lambda: self.ledger._create_run(
                run_id, self.tenant_id, self.project_id, self.task_id, self.workflow_id,
                workflow_version, event, now, deadline_at, SOURCE_LOCK_SHA256,
            ),
        )

    def append_event(self, event: WorkflowEvent, run_id: str | None,
                     now: datetime) -> AccessDecision:
        require(event.tenant_id == self.tenant_id, "EVENT_TENANT_MISMATCH")
        request = self._request("workflow.event.append", event.event_id, event.digest(), now)
        return self._execute(request, lambda: self.ledger._append_event(event, run_id))

    def transition(self, run_id: str, target: str, event_id: str | None, now: datetime,
                   expected_revision: int, payload_sha256: str,
                   lease_owner: str | None = None, lease_epoch: int | None = None,
                   reconciliation_ref: str | None = None) -> AccessDecision:
        request = self._request("workflow.run.transition", run_id, payload_sha256, now)
        return self._execute(
            request,
            lambda: self.ledger._transition(
                run_id, self.tenant_id, target, event_id, now, expected_revision,
                lease_owner, lease_epoch, reconciliation_ref,
            ),
        )

    def claim_lease(self, run_id: str, owner: str, now: datetime,
                    ttl_seconds: int = 30) -> AccessDecision:
        request = self._request("workflow.run.lease", run_id, self._payload(), now)
        return self._execute(
            request,
            lambda: self.ledger._claim_lease(
                run_id, self.tenant_id, owner, now, ttl_seconds
            ),
        )

    def recover(self, now: datetime) -> AccessDecision:
        request = self._request("workflow.recovery.run", self.tenant_id, self._payload(), now)
        return self._execute(request, lambda: self.ledger._recover(self.tenant_id, now))

    def enqueue_outbox(self, run_id: str, event_id: str, payload_ref: str,
                       now: datetime) -> AccessDecision:
        request = self._request("workflow.outbox.enqueue", run_id, self._payload(), now)
        return self._execute(
            request,
            lambda: self.ledger._enqueue_outbox(
                run_id, self.tenant_id, event_id, payload_ref, now
            ),
        )

    def dead_letter(self, run_id: str, reason: str, sanitized_ref: str,
                    now: datetime) -> AccessDecision:
        request = self._request("workflow.dlq.record", run_id, self._payload(), now)
        return self._execute(
            request,
            lambda: self.ledger._dead_letter(
                run_id, self.tenant_id, reason, sanitized_ref, now
            ),
        )

    def set_flags(self, run_id: str, now: datetime, stale: bool | None = None,
                  revoked: bool | None = None) -> AccessDecision:
        request = self._request("workflow.run.flags", run_id, self._payload(), now)
        return self._execute(
            request,
            lambda: self.ledger._set_flags(run_id, self.tenant_id, now, stale, revoked),
        )

    def reconcile(self, run_id: str, outcome: str, evidence_ref: str,
                  now: datetime, expected_revision: int, payload_sha256: str,
                  lease_owner: str | None = None, lease_epoch: int | None = None) -> AccessDecision:
        request = self._request("workflow.run.reconcile", run_id, payload_sha256, now)
        return self._execute(
            request,
            lambda: self.ledger._transition(
                run_id, self.tenant_id, outcome, None, now, expected_revision,
                lease_owner, lease_epoch, evidence_ref,
            ),
        )

    def _payload(self) -> str:
        return "a" * 64
