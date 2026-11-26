"""Strict offline policy baseline and deterministic validation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .contracts import SecurityError, require
from .network import NetworkPolicy, validate_network_policy

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_POLICY = {
    "schema": "nexlabs.security-policy.v1",
    "mode": "OFFLINE_CONTRACT_ONLY",
    "policy_epoch": 1,
    "default_effect": "DENY",
    "max_additional_spend_usd": "0",
    "external_effects": "DENY",
    "identity": {
        "required_claims": ["principal_id", "kind", "tenant_id", "project_id", "host_id", "policy_epoch"],
        "allow_role_inheritance": False,
        "hierarchy_grants": False,
        "tenant_match": "EXACT",
    },
    "authorization": {
        "grant_dimensions": ["principal_id", "action", "target_id", "tenant_id", "project_id", "task_id",
                             "workflow_id", "skill_id", "host_id", "provider_id", "risk", "policy_sha256",
                             "policy_epoch"],
        "unknown_claims": "DENY",
        "revoked_grants": "DENY",
        "expired_grants": "DENY",
        "stale_policy": "DENY",
        "grant_inheritance": False,
    },
    "approvals": {
        "required_for": ["HIGH_ASSURANCE"],
        "approver_kind": "human",
        "authorized_roles": ["OWNER", "AUTHORIZED_REVIEWER"],
        "self_approval": False,
        "binds": ["approval_id", "actor_id", "approver_id", "approver_kind", "approver_role",
                  "action", "target_id", "tenant_id", "project_id", "task_id",
                  "workflow_id", "skill_id", "host_id", "provider_id", "risk",
                  "payload_sha256", "policy_sha256", "evidence_refs", "max_spend_usd",
                  "nonce", "issued_at", "expires_at"],
        "signature_verifier": "PLUGGABLE_UNSELECTED",
        "nonce_store": "DURABLE_PROVIDER_REQUIRED",
        "hmac_adapter": "TEST_ONLY",
    },
    "network": {
        "transport": None,
        "allowed_cidrs": [],
        "peers": [],
        "services": [],
        "public_routes": False,
        "wildcard_binds": False,
        "live_configuration": False,
    },
    "secrets": {
        "provider_candidates": [],
        "opaque_references_only": True,
        "resolve_values": False,
        "create_or_rotate": False,
        "export_to_agents": False,
    },
    "isolation": {
        "workspace_scope": ["tenant_id", "project_id", "task_id"],
        "symlink_policy": "DENY",
        "reparse_policy": "DENY",
        "cross_tenant": "DENY",
        "host_mounts": "DENY",
        "docker_socket": "DENY",
    },
}


def canonical_bytes(document: object) -> bytes:
    return (json.dumps(document, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _reject_constant(_value):
    raise SecurityError("NONFINITE_POLICY_NUMBER")


def read_policy(path: Path = ROOT / "security" / "policy.json") -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=_unique_object,
                          parse_constant=_reject_constant)
    except OSError as exc:
        raise SecurityError("POLICY_FILE_UNAVAILABLE") from exc


def policy_fingerprint(policy: dict = EXPECTED_POLICY) -> str:
    return hashlib.sha256(canonical_bytes(policy)).hexdigest()


def verify_policy(policy: dict) -> None:
    require(canonical_bytes(policy) == canonical_bytes(EXPECTED_POLICY),
            "POLICY_DRIFT_OR_GRANT")
    validate_network_policy(NetworkPolicy())


def verify(root: Path = ROOT) -> None:
    policy = read_policy(Path(root) / "security" / "policy.json")
    verify_policy(policy)
