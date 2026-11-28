"""Deterministic offline compiler and per-run DAG for the 62 workflow catalog."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from security.contracts import require, require_id, require_utc

from .contracts import (
    C12_WORKFLOW_IDS, ROOT, WORKFLOW_VERSION, WorkflowError, canonical_bytes,
    forbidden_field_count, load_workflows, validate_c12, validate_c12_workflow,
    validate_workflow_catalog,
)
from .schema_validation import validate_document

SOURCE_LOCK_SHA256 = "a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e"
WORKFLOW_SOURCE = "sources/NexLabs_Workflows/workflows.json"


def _workflow_source_hash(root: Path) -> str:
    try:
        return hashlib.sha256((root / WORKFLOW_SOURCE).read_bytes()).hexdigest()
    except OSError as exc:
        raise WorkflowError("WORKFLOW_SOURCE_UNAVAILABLE") from exc


def validate_dag(nodes: list[dict[str, Any]], edges: list[tuple[str, str]]) -> None:
    ids = [node["id"] for node in nodes]
    require(len(ids) == len(set(ids)) and ids, "DAG_NODES_INVALID")
    graph = defaultdict(list)
    indegree = dict.fromkeys(ids, 0)
    for source, target in edges:
        require(source in indegree and target in indegree, "DAG_EDGE_UNKNOWN")
        graph[source].append(target)
        indegree[target] += 1
    queue = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for target in sorted(graph[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    require(visited == len(ids), "DAG_CYCLE")


def compile_catalog(root: Path = ROOT) -> dict[str, Any]:
    workflows = sorted(load_workflows(root).values(), key=lambda item: item["id"])
    validate_workflow_catalog(workflows)
    contracts = validate_c12(root)
    known = {item["id"] for item in workflows}
    compiled = []
    for workflow in workflows:
        steps = workflow.get("steps") or []
        require(bool(steps), "WORKFLOW_STEPS_EMPTY")
        agents = []
        for step in steps:
            require(isinstance(step, dict), "WORKFLOW_STEP_INVALID")
            require_id(step.get("agent_id"), "WORKFLOW_STEP_AGENT_INVALID")
            agents.append(step["agent_id"])
        if workflow["id"] in C12_WORKFLOW_IDS:
            require(workflow["dispatch_agent"] not in agents, "C12_DISPATCHER_EXECUTES")
            require(workflow.get("reviewer") != workflow["dispatch_agent"],
                    "C12_DISPATCHER_REVIEWS")
        require(set(workflow.get("next_candidates", [])) <= known, "WORKFLOW_EDGE_UNKNOWN")
        compiled.append({
            "id": workflow["id"], "name": workflow["name"], "gate": workflow["gate"],
            "risk": workflow["risk"], "activation": workflow["activation"],
            "qualification": workflow["qualification"],
            "dispatch_agent": workflow["dispatch_agent"],
            "accountable": workflow["accountable"], "reviewer": workflow["reviewer"],
            "steps": [{
                "step": step["step"], "agent_id": step["agent_id"],
                "task": step["task"], "scope": step["scope"],
                "autonomy_ceiling": step["autonomy_ceiling"],
                "eligible_packages": sorted(step.get("eligible_packages", [])),
                "external_effects": step["external_effects"],
            } for step in steps],
            "next_candidates": sorted(workflow.get("next_candidates", [])),
            "eligible_packages_union": sorted(workflow.get("eligible_packages_union", [])),
            "new_spend_limit_usd": workflow["new_spend_limit_usd"],
            "effect_policy": workflow["effect_policy"],
        })
    gates = Counter(item["gate"] for item in compiled)
    summary = {
        "workflows": len(compiled),
        "internal_only": gates["INTERNAL_ONLY"],
        "policy_gated_external": gates["POLICY_GATED_EXTERNAL"],
        "human_approval_required": gates["HUMAN_APPROVAL_REQUIRED"],
        "disabled": sum(item["activation"] == "DISABLED" for item in compiled),
        "c12": len(contracts), "grants": forbidden_field_count(workflows),
    }
    return {
        "schema": "nexlabs.workflow-compiled.v1", "source_lock_sha256": SOURCE_LOCK_SHA256,
        "workflow_source_sha256": _workflow_source_hash(root),
        "summary": summary, "c12": contracts, "workflows": compiled,
    }


def compile_run(workflow_id: str, run_id: str, tenant_id: str, now: datetime,
                deadline_at: datetime, root: Path = ROOT) -> dict[str, Any]:
    require_id(workflow_id, "WORKFLOW_ID_INVALID")
    require_id(run_id, "RUN_ID_INVALID")
    require_id(tenant_id, "TENANT_ID_INVALID")
    require_utc(now)
    require_utc(deadline_at)
    require(deadline_at > now, "RUN_DEADLINE_INVALID")
    workflows = load_workflows(root)
    require(workflow_id in workflows, "WORKFLOW_UNKNOWN")
    workflow = workflows[workflow_id]
    if workflow_id in C12_WORKFLOW_IDS:
        validate_c12_workflow(workflow)
    require(workflow.get("activation") == "DISABLED", "WORKFLOW_ACTIVATION_FORBIDDEN")
    steps = sorted(workflow.get("steps") or [], key=lambda item: item["step"])
    require(bool(steps), "WORKFLOW_STEPS_EMPTY")
    nodes = []
    for step in steps:
        require(step.get("external_effects") == "DENY", "WORKFLOW_EFFECT_DENIED")
        nodes.append({
            "id": f"step-{step['step']}", "step": step["step"],
            "agent_id": step["agent_id"], "task": step["task"],
            "scope": step["scope"], "autonomy_ceiling": step["autonomy_ceiling"],
            "eligible_packages": sorted(step.get("eligible_packages", [])),
            "external_effects": "DENY",
        })
    edges = [(nodes[index]["id"], nodes[index + 1]["id"]) for index in range(len(nodes) - 1)]
    validate_dag(nodes, edges)
    document = {
        "schema": "nexlabs.workflow-plan.v1", "run_id": run_id, "tenant_id": tenant_id,
        "workflow_id": workflow_id, "workflow_version": WORKFLOW_VERSION,
        "source_lock_sha256": SOURCE_LOCK_SHA256,
        "workflow_source_sha256": _workflow_source_hash(root),
        "now": now.isoformat(), "deadline": deadline_at.isoformat(),
        "gate": workflow["gate"], "risk": workflow["risk"],
        "activation": workflow["activation"], "qualification": workflow["qualification"],
        "accountable": workflow["accountable"], "reviewer": workflow["reviewer"],
        "dispatch_agent": workflow["dispatch_agent"],
        "execution_allowed": False, "external_effects": "DENY",
        "new_spend_limit_usd": 0, "actual_effects": 0,
        "dag": {"nodes": nodes, "edges": [{"from": a, "to": b} for a, b in edges]},
    }
    validate_document(document, ROOT / "workflow/schemas/plan-v1.json")
    return document


def dry_run(workflow_id: str, run_id: str, tenant_id: str, now: datetime,
            deadline_at: datetime, root: Path = ROOT) -> dict[str, Any]:
    return compile_run(workflow_id, run_id, tenant_id, now, deadline_at, root)


def compile_bytes(document: dict[str, Any]) -> bytes:
    return canonical_bytes(document)
