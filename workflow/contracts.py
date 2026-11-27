"""Offline workflow event, state and C12 contracts for NLE-WF-WO-001."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from security.contracts import (
    RISKS, SecurityError, require, require_hash, require_id, require_utc,
)

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = "sources/NexLabs_Workflows/workflows.json"
SCHEMA_VERSION = "nexlabs.event.v1"
EVENT_TYPES = frozenset({
    "lead.qualified", "proposal.approved", "contract.signed", "work_order.ready",
    "pr.audited", "release.validated", "product.qa_passed", "campaign.draft_ready",
    "order.confirmed", "refund.confirmed", "research.validated",
    "simulation.completed", "incident.opened",
})
CLASSIFICATIONS = frozenset({"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"})
STATES = frozenset({
    "RECEIVED", "VALIDATED", "QUEUED", "RUNNING", "REVIEW", "APPROVED",
    "CORRECTION_REQUIRED", "BLOCKED", "WAITING_APPROVAL", "EFFECT_READY",
    "EFFECT_IN_PROGRESS", "VERIFIED", "COMPLETED", "STALE", "CANCELLED",
    "RETRY_WAIT", "UNKNOWN_EFFECT", "FAILED", "QUARANTINED",
})
TERMINAL = frozenset({"COMPLETED", "CANCELLED", "QUARANTINED"})
TRANSITIONS = {
    "RECEIVED": frozenset({"VALIDATED", "QUARANTINED", "FAILED"}),
    "VALIDATED": frozenset({"QUEUED", "BLOCKED", "QUARANTINED"}),
    "QUEUED": frozenset({"RUNNING", "CANCELLED", "BLOCKED"}),
    "RUNNING": frozenset({"REVIEW", "FAILED", "RETRY_WAIT", "WAITING_APPROVAL", "BLOCKED"}),
    "REVIEW": frozenset({"APPROVED", "CORRECTION_REQUIRED", "BLOCKED"}),
    "APPROVED": frozenset({"VERIFIED", "EFFECT_READY", "COMPLETED"}),
    "CORRECTION_REQUIRED": frozenset({"QUEUED", "CANCELLED", "BLOCKED"}),
    "WAITING_APPROVAL": frozenset({"APPROVED", "CORRECTION_REQUIRED", "BLOCKED", "CANCELLED"}),
    "EFFECT_READY": frozenset({"EFFECT_IN_PROGRESS", "CANCELLED"}),
    "EFFECT_IN_PROGRESS": frozenset({"VERIFIED", "UNKNOWN_EFFECT", "FAILED"}),
    "UNKNOWN_EFFECT": frozenset({"VERIFIED", "FAILED", "BLOCKED"}),
    "RETRY_WAIT": frozenset({"QUEUED", "FAILED", "CANCELLED"}),
    "STALE": frozenset({"QUEUED", "CANCELLED", "BLOCKED"}),
    "FAILED": frozenset({"RETRY_WAIT", "QUARANTINED", "CANCELLED"}),
    "VERIFIED": frozenset({"COMPLETED"}),
    "COMPLETED": frozenset(),
    "CANCELLED": frozenset(),
    "QUARANTINED": frozenset(),
}
C12_WORKFLOW_IDS = frozenset({
    "NLE-WF-GOV-03", "NLE-WF-QNT-01", "NLE-WF-QNT-02",
    "NLE-WF-QNT-03", "NLE-WF-QNT-05",
})
MAX_ATTEMPTS = 2


class WorkflowError(SecurityError):
    """A fail-closed workflow contract violation."""


def canonical_bytes(document: Any) -> bytes:
    return (json.dumps(document, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise WorkflowError("WORKFLOW_SOURCE_UNAVAILABLE") from exc


@dataclass(frozen=True)
class WorkflowEvent:
    event_id: str
    event_type: str
    occurred_at: datetime
    received_at: datetime
    producer: str
    subject_ref: str
    tenant_id: str
    correlation_id: str
    idempotency_key: str
    payload_ref: str
    payload_sha256: str
    data_classification: str
    risk: str
    schema_version: str = SCHEMA_VERSION

    def validate(self) -> None:
        require(self.schema_version == SCHEMA_VERSION, "EVENT_SCHEMA_INVALID")
        require(self.event_type in EVENT_TYPES, "EVENT_TYPE_INVALID")
        for value in (
            self.event_id, self.producer, self.subject_ref, self.tenant_id,
            self.correlation_id, self.idempotency_key, self.payload_ref,
        ):
            require_id(value, "EVENT_IDENTIFIER_INVALID")
        require_utc(self.occurred_at)
        require_utc(self.received_at)
        require(self.received_at >= self.occurred_at, "EVENT_RECEIVED_BEFORE_OCCURRED")
        require_hash(self.payload_sha256)
        require(self.data_classification in CLASSIFICATIONS, "EVENT_CLASSIFICATION_INVALID")
        require(self.risk in RISKS, "EVENT_RISK_INVALID")
        require(not self.payload_ref.startswith(("http:", "https:", "file:")),
                "EVENT_PAYLOAD_REF_MUST_BE_OPAQUE")

    def canonical(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "received_at": self.received_at.isoformat(),
            "producer": self.producer,
            "subject_ref": self.subject_ref,
            "tenant_id": self.tenant_id,
            "correlation_id": self.correlation_id,
            "idempotency_key": self.idempotency_key,
            "payload_ref": self.payload_ref,
            "payload_sha256": self.payload_sha256,
            "data_classification": self.data_classification,
            "risk": self.risk,
        }

    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self.canonical())).hexdigest()


def validate_event(event: WorkflowEvent) -> None:
    require(isinstance(event, WorkflowEvent), "EVENT_TYPE_OBJECT_REQUIRED")
    event.validate()


def assert_transition(current: str, target: str) -> None:
    require(current in STATES and target in STATES, "STATE_UNKNOWN")
    require(target in TRANSITIONS[current], "STATE_TRANSITION_FORBIDDEN")


def retry_decision(status_code: int, attempts: int, retry_after: int | None = None) -> str:
    require(type(status_code) is int and type(attempts) is int and attempts >= 0,
            "RETRY_INPUT_INVALID")
    require(retry_after is None or (type(retry_after) is int and retry_after >= 0),
            "RETRY_INPUT_INVALID")
    if status_code in (401, 403):
        return "BLOCK"
    if status_code == 429:
        return "RETRY_AFTER" if retry_after is not None else "RETRY_WAIT"
    if status_code in (408, 500, 502, 503, 504):
        return "RETRY_WAIT" if attempts < MAX_ATTEMPTS else "FAILED"
    return "FAILED"


def load_workflows(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    document = _read_json(root / WORKFLOWS)
    workflows = document.get("workflows")
    require(isinstance(workflows, list), "WORKFLOW_CATALOG_INVALID")
    result = {item["id"]: item for item in workflows if isinstance(item, dict) and "id" in item}
    require(len(result) == len(workflows), "WORKFLOW_DUPLICATE_ID")
    return result


def validate_c12_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    require(workflow.get("activation") == "DISABLED", "C12_ACTIVATION_FORBIDDEN")
    require(workflow.get("gate") == "INTERNAL_ONLY", "C12_GATE_FORBIDDEN")
    require(workflow.get("effect_policy") == "DENY_DEFAULT", "C12_EFFECT_FORBIDDEN")
    require(workflow.get("new_spend_limit_usd") == 0, "C12_SPEND_FORBIDDEN")
    require(workflow.get("qualification") == "NOT_RUN", "C12_QUALIFICATION_FORBIDDEN")
    dispatcher = workflow.get("dispatch_agent")
    require_id(dispatcher, "C12_DISPATCHER_INVALID")
    steps = workflow.get("steps") or []
    require(isinstance(steps, list) and steps, "C12_STEPS_INVALID")
    step_agents = {step.get("agent_id") for step in steps if isinstance(step, dict)}
    require(dispatcher not in step_agents, "C12_DISPATCHER_EXECUTES")
    require(dispatcher != workflow.get("reviewer"), "C12_DISPATCHER_REVIEWS")
    require(dispatcher != workflow.get("accountable"), "C12_DISPATCHER_ACCOUNTABLE")
    for step in steps:
        require(isinstance(step, dict), "C12_STEP_INVALID")
        require(step.get("external_effects") == "DENY", "C12_STEP_EFFECT_FORBIDDEN")
        require(step.get("agent_id") != dispatcher, "C12_DISPATCHER_EXECUTES")
    return {
        "workflow_id": workflow["id"], "dispatcher": dispatcher,
        "accountable": workflow.get("accountable"), "reviewer": workflow.get("reviewer"),
        "execution_agents": sorted(step_agents), "dispatch_only": True,
        "skill_imports": [], "memory_grants": [], "client_access": False,
        "activation": "DISABLED", "effect_policy": "DENY_DEFAULT",
        "new_spend_limit_usd": 0,
    }


def validate_c12(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    workflows = load_workflows(root)
    require(C12_WORKFLOW_IDS <= set(workflows), "C12_WORKFLOW_MISSING")
    return {wid: validate_c12_workflow(workflows[wid]) for wid in sorted(C12_WORKFLOW_IDS)}
