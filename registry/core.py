"""Offline, fail-closed compiler for the immutable NexLabs source catalog.

This module produces specification locks, not executable skills or Paperclip
API payloads. It has no network, credential, process or runtime mutation code.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

from scripts.validate_sources import validate as validate_source_pack

ROOT = Path(__file__).resolve().parents[1]
SOURCE_LOCK_SHA256 = "a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e"
SOURCE_LOCK = "locks/source-lock.json"
CATALOG = "sources/NexLabs_AI_Enterprise_Agent_Catalog.json"
SR = "sources/NexLabs_Skills_Registry"
CEO = "NLE-ZEUS-CEO"
EXPECTED_POLICY = json.loads('''{"schema":"nexlabs.registry-policy.v1","mode":"OFFLINE_ONLY","default_effect":"DENY","allow_network":false,"allow_runtime_writes":false,"allow_model_calls":false,"allow_source_downloads":false,"allow_skill_activation":false,"allow_agent_activation":false,"allow_heartbeat":false,"max_additional_spend_usd":0,"tool_grants":[],"credential_grants":[],"required_source_evidence":["immutable_commit","sha256","artifact_license","inventory","reviewed_diff","independent_review"],"runtime_gates":["POST_AUTH_BACKUP","LEAST_PRIVILEGE_GRANTS","C12","EXPLICIT_OWNER_APPROVAL"]}''')


class RegistryError(ValueError):
    """A validation failure. No promotion or runtime action follows."""


def require(condition, reason):
    if not condition:
        raise RegistryError(reason)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(document):
    return (json.dumps(document, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _reject_constant(_value):
    raise RegistryError("NONFINITE_JSON_NUMBER")


def read_json(path, root):
    """Read JSON only after resolving it beneath root without links or escapes."""
    root = Path(root).resolve()
    candidate = Path(path)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise RegistryError("DOCUMENT_NOT_FOUND") from exc
    try:
        relative = resolved.relative_to(root)
    except ValueError as exc:
        raise RegistryError("UNSAFE_DOCUMENT_PATH") from exc
    safe = safe_path(root, relative.as_posix())
    return json.loads(safe.read_text(encoding="utf-8-sig"),
                      object_pairs_hook=_unique_object, parse_constant=_reject_constant)


def _is_link(path):
    return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400)


def safe_path(root, relative):
    """Existing regular file beneath root; reject symlinks and reparse points."""
    require(isinstance(relative, str) and "\\" not in relative and ":" not in relative,
            "UNSAFE_SOURCE_PATH")
    posix = PurePosixPath(relative)
    require(not posix.is_absolute() and bool(posix.parts)
            and relative == posix.as_posix() and ".." not in posix.parts,
            "UNSAFE_SOURCE_PATH")
    current = root
    for part in posix.parts:
        current = current / part
        try:
            linked = _is_link(current)
        except OSError as exc:
            raise RegistryError("SOURCE_NOT_REGULAR") from exc
        require(not linked, "SOURCE_LINK_FORBIDDEN")
    require(current.is_file() and current.resolve().is_relative_to(root.resolve()),
            "SOURCE_NOT_REGULAR")
    return current


def index(rows, field):
    result = {item[field]: item for item in rows}
    require(len(result) == len(rows), "DUPLICATE_IDENTIFIER")
    return result


def verify_policy(policy):
    require(canonical_bytes(policy) == canonical_bytes(EXPECTED_POLICY),
            "POLICY_DRIFT_OR_GRANT")


def validate_dependencies(packages):
    active, done = set(), set()

    def visit(pid):
        require(pid in packages, "UNKNOWN_PACKAGE_DEPENDENCY")
        require(pid not in active, "PACKAGE_DEPENDENCY_CYCLE")
        if pid in done:
            return
        active.add(pid)
        deps = packages[pid]["dependencies"]
        require(len(deps) == len(set(deps)), "DUPLICATE_DEPENDENCY")
        for dep in deps:
            visit(dep)
        active.remove(pid)
        done.add(pid)

    for pid in sorted(packages):
        visit(pid)


def _verified_sources(root):
    path = safe_path(root, SOURCE_LOCK)
    require(sha256(path.read_bytes()) == SOURCE_LOCK_SHA256, "BASELINE_LOCK_DRIFT")
    source_files = read_json(path, root)["files"]
    require(len(source_files) == 364, "BASELINE_SOURCE_COUNT")
    for relative, expected in source_files.items():
        require(relative.startswith("sources/"), "UNSAFE_SOURCE_LOCK_ENTRY")
        require(sha256(safe_path(root, relative).read_bytes()) == expected,
                "SOURCE_FINGERPRINT_MISMATCH")
    for path in (root / "sources").rglob("*"):
        require(not _is_link(path), "SOURCE_LINK_FORBIDDEN")
    # Reuse the established cross-plan, archive and referential integrity gate.
    validate_source_pack(root, verbose=False)
    return source_files


def build(root=ROOT):
    root = Path(root)
    hashes = _verified_sources(root)
    policy = read_json(safe_path(root, "registry/policy.json"), root)
    verify_policy(policy)
    catalog = read_json(safe_path(root, CATALOG), root)
    original = read_json(safe_path(root, f"{SR}/registry.json"), root)
    bindings = read_json(safe_path(root, f"{SR}/agent-bindings.json"), root)
    with safe_path(root, f"{SR}/assignment-matrix.csv").open(
            encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    agents = index(catalog["agents"], "id")
    packages = index(original["packages"], "id")
    competencies = index(original["competencies"], "id")
    assignments = index(rows, "assignment_id")
    sources = index(original["sources"], "id")
    require((len(agents), len(packages), len(competencies), len(assignments), len(sources))
            == (105, 92, 1071, 1110, 18), "CANONICAL_COUNT_DRIFT")
    require(set(bindings) == set(agents), "BINDING_COVERAGE")
    require(Counter(p["type"] for p in packages.values()) == {"domain": 80, "shared": 12},
            "PACKAGE_TYPE_DRIFT")
    require(len({row["original_competency"] for row in rows}) == 996, "LABEL_COUNT_DRIFT")
    require(sum(len(a["qualification_tests"]) for a in agents.values()) == 316,
            "QUALIFICATION_TEST_COUNT_DRIFT")
    require(Counter((row["agent_id"], row["original_competency"]) for row in rows)
            == Counter((aid, skill) for aid, a in agents.items() for skill in a["skills"]),
            "ASSIGNMENT_CONTENT_DRIFT")
    validate_dependencies(packages)

    by_agent, by_package = defaultdict(list), defaultdict(list)
    for row in rows:
        require(row["status"] == "PLANNED_NOT_QUALIFIED", "ASSIGNMENT_STATUS_DRIFT")
        require(row["department"] == agents[row["agent_id"]]["department"],
                "ASSIGNMENT_DEPARTMENT_DRIFT")
        by_agent[row["agent_id"]].append(row)
        by_package[row["package_id"]].append(row)

    quarantine = []
    for sid, source in sorted(sources.items()):
        expected_status = "PROPOSED_INTERNAL" if sid == "OWN" else "CANDIDATE_NOT_APPROVED"
        require(source["status"] == expected_status
                and source["commit_sha"] is None and source["content_sha256"] is None,
                "UNREVIEWED_SOURCE_PROMOTION")
        quarantine.append({
            "source_id": sid, "source_status": source["status"],
            "state": "AUTHORING_REQUIRED" if sid == "OWN" else "QUARANTINED",
            "license_observation": source["license_observation"],
            "artifact_license_verified": False, "commit_sha": None,
            "content_sha256": None, "download_allowed": False,
            "execution_allowed": False,
            "required_evidence": policy["required_source_evidence"],
        })
    require(sum(q["state"] == "QUARANTINED" for q in quarantine) == 17,
            "QUARANTINE_COUNT_DRIFT")

    manifests = {}
    for pid, package in sorted(packages.items()):
        require(bool(re.fullmatch(r"[a-z][a-z0-9-]*", pid)), "INVALID_PACKAGE_ID")
        require(package["status"] == "SPECIFIED_NOT_QUALIFIED"
                and package["version"] == "0.1.0-proposed"
                and package["tool_grants"] == [] and package["artifact_sha256"] is None,
                "UNQUALIFIED_PACKAGE_PROMOTION")
        spec = f"{SR}/packages/{pid}/SPEC.md"
        require(spec in hashes, "MISSING_LOCKED_SPEC")
        manifests[pid] = {
            "package_id": pid, "type": package["type"], "version": package["version"],
            "state": package["status"], "spec_path": spec, "spec_sha256": hashes[spec],
            "artifact_sha256": None, "risk": package["risk"],
            "review_owner": package["review_owner"],
            "source_ids": sorted(package["sources"]),
            "dependencies": sorted(package["dependencies"]),
            "competency_ids": sorted(package["competency_ids"]),
            "assignment_ids": sorted(row["assignment_id"] for row in by_package[pid]),
            "qualification_test_ids": sorted(package["qualification_test_ids"]),
            "tool_grants": [], "credential_grants": [],
            "execution_allowed": False, "import_allowed": False,
        }

    locks = {}
    for aid, agent in sorted(agents.items()):
        binding = bindings[aid]
        require(agent["enabled"] is False and agent["heartbeat_enabled"] is False
                and agent["new_spend_authorized"] is False
                and agent["resolved_model_id"] is None
                and agent["external_effects_default"] == "DENY"
                and binding["enabled"] is False, "UNSAFE_AGENT_BASELINE")
        require(all(test["status"] == "NOT_RUN" for test in agent["qualification_tests"]),
                "UNQUALIFIED_AGENT_TEST_STATE")
        locked = {
            "agent_id": aid, "state": "PLANNED_NOT_QUALIFIED",
            "source_sha256": hashes[CATALOG],
            "model_profile_candidate": binding["model_profile"],
            "resolved_model_id": None, "adapter": None,
            "autonomy_ceiling_candidate": binding["autonomy_ceiling"],
            "package_specs": [
                {"package_id": pid, "version": manifests[pid]["version"],
                 "spec_sha256": manifests[pid]["spec_sha256"], "artifact_sha256": None}
                for pid in sorted(binding["packages"])
            ],
            "assignment_ids": sorted(row["assignment_id"] for row in by_agent[aid]),
            "qualification_test_ids": sorted(test["id"] for test in agent["qualification_tests"]),
            "enabled": False, "heartbeat_enabled": False, "tool_grants": [],
            "credential_grants": [], "external_effects": "DENY",
            "max_additional_spend_usd": 0,
        }
        locks[aid] = {**locked, "lock_sha256": sha256(canonical_bytes(locked))}

    require(sum(len(lock["package_specs"]) for lock in locks.values()) == 183,
            "AGENT_PACKAGE_LINK_COUNT_DRIFT")
    return {
        "schema": "nexlabs.offline-registry.v1", "state": "SPECIFICATIONS_ONLY",
        "source_lock_sha256": SOURCE_LOCK_SHA256, "policy": policy,
        "summary": {"agents": 105, "packages": 92, "assignments": 1110,
                    "contextual_competencies": 1071, "qualification_tests": 316,
                    "agent_package_links": 183, "quarantined_external_sources": 17,
                    "qualified_packages": 0, "active_agents": 0},
        "manifests": manifests, "agent_locks": locks,
        "assignments": [assignments[key] for key in sorted(assignments)],
        "competencies": [competencies[key] for key in sorted(competencies)],
        "shared_core_baseline": original["shared_core_baseline"],
        "quarantine": quarantine,
    }


def provision_plan(root=ROOT, bundle=None):
    """Compile topologically ordered intentions, never an executable API request."""
    root = Path(root)
    expected = build(root)
    if bundle is not None:
        require(canonical_bytes(bundle) == canonical_bytes(expected), "REGISTRY_LOCK_DRIFT")
    agents = index(read_json(safe_path(root, CATALOG), root)["agents"], "id")

    def depth(aid):
        seen = set()
        while aid is not None:
            require(aid in agents and aid not in seen, "INVALID_HIERARCHY")
            seen.add(aid)
            aid = agents[aid]["reports_to"]
        require(CEO in seen, "MISSING_CEO_ANCESTOR")
        return len(seen)

    intents = []
    for aid in sorted(agents, key=lambda key: (depth(key), key)):
        a = agents[aid]
        intents.append({
            "canonical_id": aid, "department": a["department"], "role": a["role"],
            "reports_to": a["reports_to"],
            "independent_escalation_to_owner": a["independent_escalation_to_owner"],
            "intent": "RECONCILE_EXISTING_BEFORE_CREATE" if aid == CEO else "PLAN_IF_ABSENT",
            "runtime_id": None, "runtime_match_verified": False,
            "lock_sha256": expected["agent_locks"][aid]["lock_sha256"],
            "status": "PAUSED_REQUIRED", "enabled": False, "heartbeat_enabled": False,
            "model_id": None, "adapter": None, "skill_imports": [],
            "tool_grants": [], "credential_grants": [], "external_effects": "DENY",
            "max_additional_spend_usd": 0,
        })
    return {
        "schema": "nexlabs.provision-dry-run.v1", "mode": "DRY_RUN_ONLY",
        "registry_sha256": sha256(canonical_bytes(expected)),
        "policy": expected["policy"], "agent_intents": intents,
        "runtime_inventory_verified": False, "actual_creates": 0,
        "actual_updates": 0, "actual_model_calls": 0,
        "blocking_gates": ["RUNTIME_IDENTITY_RECONCILIATION", "QUALIFIED_SKILLS",
                           "SUPPORTED_PAPERCLIP_API", "LEAST_PRIVILEGE_GRANTS",
                           "POST_AUTH_BACKUP", "C12", "EXPLICIT_OWNER_APPROVAL"],
    }


def verify_document(document, root=ROOT):
    """Exact structural/content verification against the canonical compiler.

    Unknown fields, types, modified locks, grants and status changes all fail.
    The JSON schemas describe the envelopes; this check is stricter.
    """
    require(isinstance(document, dict), "INVALID_DOCUMENT")
    schema = document.get("schema")
    if schema == "nexlabs.offline-registry.v1":
        expected = build(root)
    elif schema == "nexlabs.provision-dry-run.v1":
        expected = provision_plan(root)
    else:
        raise RegistryError("UNSUPPORTED_SCHEMA")
    require(canonical_bytes(document) == canonical_bytes(expected),
            "CANONICAL_DOCUMENT_MISMATCH")
    return True
