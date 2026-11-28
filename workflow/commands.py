"""Single authorized command boundary for the offline workflow ledger."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import hashlib
from typing import Any

from security.approval import SignatureVerifier
from security.contracts import (
    AccessDecision, AccessRequest, ApprovalEnvelope, Grant, Principal, require,
)

from .authorization import authorize_workflow
from .contracts import (
    C12_WORKFLOW_IDS, WORKFLOW_VERSION, RunOptions, WorkflowEvent, canonical_bytes,
    load_workflows, require_risk_floor, validate_c12_workflow,
)
from .ledger import Ledger

SOURCE_LOCK_SHA256 = "a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e"


def _payload_digest(operation: str, **values: Any) -> str:
    document = {"operation": operation, **values}
    return hashlib.sha256(canonical_bytes(document)).hexdigest()


class _BoundNonceStore:
    def __init__(self, ledger: Ledger, run_id: str | None, tenant_id: str,
                 approval_id: str | None):
        self._ledger = ledger
        self.run_id = run_id
        self.tenant_id = tenant_id
        self.approval_id = approval_id

    def consume(self, nonce: str, expires_at: datetime, now: datetime) -> bool:
        return self._ledger._consume(
            nonce, expires_at, now, self.run_id, self.tenant_id, self.approval_id,
        )


@dataclass(frozen=True)
class CommandScope:
    """Immutable execution scope shared by every command in one boundary."""

    actor: Principal
    tenant_id: str
    project_id: str
    task_id: str
    workflow_id: str


class WorkflowCommands:
    """The only public mutation boundary. Ledger primitives stay private."""

    def __init__(
        self,
        ledger: Ledger,
        scope: CommandScope,
        *,
        policy_sha256: str,
        policy_epoch: int,
        risk: str = "STANDARD",
        grants: tuple[Grant, ...] = (),
        approval: ApprovalEnvelope | None = None,
        approval_signature: str | None = None,
        verifier: SignatureVerifier | None = None,
    ):
        self._ledger = ledger
        self._scope = scope
        self.policy_sha256 = policy_sha256
        self.policy_epoch = policy_epoch
        self.risk = risk
        self.grants = grants
        self.approval = approval
        self.approval_signature = approval_signature
        self.verifier = verifier
        self._workflow = self._canonical_workflow(scope.workflow_id)
        require_risk_floor(self.risk, self._workflow["risk"])
        require(self._workflow["activation"] == "DISABLED",
                "WORKFLOW_ACTIVATION_FORBIDDEN")
        if scope.workflow_id in C12_WORKFLOW_IDS:
            validate_c12_workflow(self._workflow)
        agents = {
            step.get("agent_id") for step in self._workflow.get("steps", [])
            if isinstance(step, dict)
        }
        require(self._workflow.get("reviewer") != self._workflow.get("accountable"),
                "WORKFLOW_REVIEWER_ACCOUNTABLE_COLLISION")
        require(self._workflow.get("reviewer") not in agents,
                "WORKFLOW_REVIEWER_EXECUTES")
        if self._workflow["gate"] == "HUMAN_APPROVAL_REQUIRED":
            require(self.risk == "HIGH_ASSURANCE",
                    "HUMAN_APPROVAL_ASSURANCE_REQUIRED")

    @staticmethod
    def _canonical_workflow(workflow_id: str) -> dict:
        workflows = load_workflows()
        require(workflow_id in workflows, "WORKFLOW_UNKNOWN")
        return workflows[workflow_id]

    @property
    def scope(self) -> CommandScope:
        return self._scope

    @property
    def actor(self) -> Principal:
        return self._scope.actor

    @property
    def tenant_id(self) -> str:
        return self._scope.tenant_id

    @property
    def project_id(self) -> str:
        return self._scope.project_id

    @property
    def task_id(self) -> str:
        return self._scope.task_id

    @property
    def workflow_id(self) -> str:
        return self._scope.workflow_id

    @property
    def _scope_tuple(self) -> tuple[str, str, str]:
        return (self.project_id, self.task_id, self.workflow_id)

    def _require_run_scope(self, run_id: str) -> dict:
        run = self._ledger.run_scoped(
            run_id, self.tenant_id, self.project_id, self.task_id, self.workflow_id,
        )
        require_risk_floor(self.risk, run["risk"])
        if run["gate"] == "HUMAN_APPROVAL_REQUIRED":
            require(self.risk == "HIGH_ASSURANCE",
                    "HUMAN_APPROVAL_ASSURANCE_REQUIRED")
        return run

    def _requires_approval(self) -> bool:
        return (self.risk == "HIGH_ASSURANCE"
                or self._workflow["gate"] == "HUMAN_APPROVAL_REQUIRED")

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

    def _execute(self, request: AccessRequest, apply: Callable[[], None],
                 run_id: str | None = None) -> AccessDecision:
        with self._ledger._transaction():
            decision = authorize_workflow(
                self._ledger, request, self.grants,
                current_policy_sha256=self.policy_sha256,
                current_policy_epoch=self.policy_epoch,
                approval=self.approval,
                approval_signature=self.approval_signature,
                verifier=self.verifier,
                nonce_store=_BoundNonceStore(
                    self._ledger, run_id, request.tenant_id,
                    self.approval.approval_id if self.approval else None,
                ),
            )
            require(decision.allowed and decision.grant_id is not None, "COMMAND_DENIED")
            apply()
            if self.approval is not None:
                require(self._requires_approval(), "APPROVAL_NOT_VERIFIED")
                self._ledger._record_approval(
                    request, self.approval, run_id, decision.reason, request.now,
                )
            return decision

    def create_run(self, run_id: str, workflow_version: str, event: WorkflowEvent,
                   now: datetime, deadline_at: datetime, *,
                   agent_id: str | None = None,
                   skill_lock_id: str | None = None,
                   skill_lock_version: str | None = None,
                   skill_lock_hash: str | None = None,
                   model_id: str | None = None,
                   output_ref: str | None = None,
                   evidence_ref: str | None = None) -> AccessDecision:
        require(event.tenant_id == self.tenant_id, "EVENT_TENANT_MISMATCH")
        require(workflow_version == WORKFLOW_VERSION, "WORKFLOW_VERSION_UNKNOWN")
        require_risk_floor(self.risk, event.risk)
        gate = self._workflow["gate"]
        payload = _payload_digest(
            "workflow.run.create", event_sha256=event.digest(),
            workflow_version=workflow_version, deadline_at=deadline_at.isoformat(),
            gate=gate, activation=self._workflow["activation"],
            policy_epoch=self.policy_epoch,
        )
        request = self._request("workflow.run.create", run_id, payload, now)
        return self._execute(
            request,
            lambda: self._ledger._create_run(
                run_id, self.tenant_id, self.project_id, self.task_id, self.workflow_id,
                workflow_version, event, now, deadline_at, SOURCE_LOCK_SHA256,
                RunOptions(
                    risk=self.risk, agent_id=agent_id, skill_lock_id=skill_lock_id,
                    skill_lock_version=skill_lock_version,
                    skill_lock_hash=skill_lock_hash, model_id=model_id,
                    output_ref=output_ref, evidence_ref=evidence_ref, gate=gate,
                ),
            ),
            run_id,
        )

    def append_event(self, event: WorkflowEvent, run_id: str | None,
                     now: datetime) -> AccessDecision:
        require(event.tenant_id == self.tenant_id, "EVENT_TENANT_MISMATCH")
        require_risk_floor(self.risk, event.risk)
        if run_id is not None:
            self._require_run_scope(run_id)
        payload = _payload_digest(
            "workflow.event.append", event_sha256=event.digest(), run_id=run_id,
            policy_epoch=self.policy_epoch,
        )
        request = self._request("workflow.event.append", event.event_id, payload, now)
        return self._execute(
            request, lambda: self._ledger._append_event(event, run_id), run_id
        )

    def transition(self, run_id: str, target: str, event_id: str | None, now: datetime,
                   expected_revision: int, payload_sha256: str,
                   lease_owner: str | None = None, lease_epoch: int | None = None,
                   reconciliation_ref: str | None = None) -> AccessDecision:
        current = self._require_run_scope(run_id)
        require(target not in {"EFFECT_READY", "EFFECT_IN_PROGRESS"},
                "WORKFLOW_DISABLED_EXECUTION")
        action = f"workflow.run.transition.{current['state']}.{target}"
        payload = _payload_digest(
            "workflow.run.transition", target=target, event_id=event_id,
            expected_revision=expected_revision, payload_sha256=payload_sha256,
            lease_owner=lease_owner, lease_epoch=lease_epoch,
            reconciliation_ref=reconciliation_ref, policy_epoch=self.policy_epoch,
            gate=current["gate"],
        )
        request = self._request(action, run_id, payload, now)
        return self._execute(
            request,
            lambda: self._ledger._transition(
                run_id, self.tenant_id, target, event_id, now, expected_revision,
                lease_owner, lease_epoch, reconciliation_ref, scope=self._scope_tuple,
            ),
            run_id,
        )

    def claim_lease(self, run_id: str, owner: str, now: datetime,
                    expected_revision: int, ttl_seconds: int = 30) -> AccessDecision:
        current = self._require_run_scope(run_id)
        action = f"workflow.run.lease.{current['state']}"
        payload = _payload_digest(
            "workflow.run.lease", owner=owner, ttl_seconds=ttl_seconds,
            expected_revision=expected_revision, policy_epoch=self.policy_epoch,
        )
        request = self._request(action, run_id, payload, now)
        return self._execute(
            request,
            lambda: self._ledger._claim_lease(
                run_id, self.tenant_id, owner, now, ttl_seconds, expected_revision,
                scope=self._scope_tuple,
            ),
            run_id,
        )

    def recover(self, now: datetime) -> AccessDecision:
        payload = _payload_digest(
            "workflow.recovery.run", tenant_id=self.tenant_id,
            project_id=self.project_id, task_id=self.task_id,
            workflow_id=self.workflow_id, policy_epoch=self.policy_epoch,
        )
        request = self._request("workflow.recovery.run", self.tenant_id, payload, now)
        return self._execute(
            request,
            lambda: self._ledger._recover(
                self.tenant_id, self.project_id, self.task_id, self.workflow_id,
                now, self.risk,
            ),
        )

    def enqueue_outbox(self, run_id: str, event_id: str, payload_ref: str,
                       now: datetime, expected_revision: int,
                       lease_owner: str | None = None,
                       lease_epoch: int | None = None) -> AccessDecision:
        current = self._require_run_scope(run_id)
        action = f"workflow.outbox.enqueue.{current['state']}"
        payload = _payload_digest(
            "workflow.outbox.enqueue", event_id=event_id, payload_ref=payload_ref,
            expected_revision=expected_revision, lease_owner=lease_owner,
            lease_epoch=lease_epoch, policy_epoch=self.policy_epoch,
        )
        request = self._request(action, run_id, payload, now)
        return self._execute(
            request,
            lambda: self._ledger._enqueue_outbox(
                run_id, self.tenant_id, event_id, payload_ref, now, expected_revision,
                lease_owner, lease_epoch, scope=self._scope_tuple,
            ),
            run_id,
        )

    def dead_letter(self, run_id: str, reason: str, sanitized_ref: str,
                    now: datetime, expected_revision: int) -> AccessDecision:
        current = self._require_run_scope(run_id)
        action = f"workflow.dlq.record.{current['state']}"
        payload = _payload_digest(
            "workflow.dlq.record", reason=reason, sanitized_ref=sanitized_ref,
            expected_revision=expected_revision, policy_epoch=self.policy_epoch,
        )
        request = self._request(action, run_id, payload, now)
        return self._execute(
            request,
            lambda: self._ledger._dead_letter(
                run_id, self.tenant_id, reason, sanitized_ref, now, expected_revision,
                scope=self._scope_tuple,
            ),
            run_id,
        )

    def set_flags(self, run_id: str, now: datetime, expected_revision: int,
                  stale: bool | None = None,
                  revoked: bool | None = None) -> AccessDecision:
        current = self._require_run_scope(run_id)
        action = f"workflow.run.flags.{current['state']}"
        payload = _payload_digest(
            "workflow.run.flags", stale=stale, revoked=revoked,
            expected_revision=expected_revision, policy_epoch=self.policy_epoch,
        )
        request = self._request(action, run_id, payload, now)
        return self._execute(
            request,
            lambda: self._ledger._set_flags(
                run_id, self.tenant_id, now, stale, revoked, expected_revision,
                scope=self._scope_tuple,
            ),
            run_id,
        )

    def reconcile(self, run_id: str, outcome: str, evidence_ref: str,
                  now: datetime, expected_revision: int, payload_sha256: str,
                  lease_owner: str | None = None,
                  lease_epoch: int | None = None) -> AccessDecision:
        current = self._require_run_scope(run_id)
        action = f"workflow.run.reconcile.{current['state']}.{outcome}"
        payload = _payload_digest(
            "workflow.run.reconcile", outcome=outcome, evidence_ref=evidence_ref,
            expected_revision=expected_revision, payload_sha256=payload_sha256,
            lease_owner=lease_owner, lease_epoch=lease_epoch,
            policy_epoch=self.policy_epoch,
        )
        request = self._request(action, run_id, payload, now)
        return self._execute(
            request,
            lambda: self._ledger._transition(
                run_id, self.tenant_id, outcome, None, now, expected_revision,
                lease_owner, lease_epoch, evidence_ref, scope=self._scope_tuple,
            ),
            run_id,
        )
