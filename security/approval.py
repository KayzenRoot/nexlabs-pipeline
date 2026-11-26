"""Bound approval-envelope verification; no signer or durable ledger is included."""
from __future__ import annotations

from datetime import datetime
import hashlib
import hmac
import json
import re
from threading import Lock
from typing import Protocol

from .contracts import (
    AccessRequest, ApprovalEnvelope, SecurityError, as_decimal, require,
    require_hash, require_id, require_utc,
)

NONCE = re.compile(r"^[A-Za-z0-9_-]{22,128}$")


def canonical_approval_bytes(envelope: ApprovalEnvelope) -> bytes:
    document = {
        "approval_id": envelope.approval_id,
        "actor_id": envelope.actor_id,
        "approver_id": envelope.approver_id,
        "approver_kind": envelope.approver_kind,
        "action": envelope.action,
        "target_id": envelope.target_id,
        "tenant_id": envelope.tenant_id,
        "payload_sha256": envelope.payload_sha256,
        "policy_sha256": envelope.policy_sha256,
        "evidence_refs": list(envelope.evidence_refs),
        "max_spend_usd": str(as_decimal(envelope.max_spend_usd)),
        "nonce": envelope.nonce,
        "issued_at": envelope.issued_at.isoformat(),
        "expires_at": envelope.expires_at.isoformat(),
    }
    return (json.dumps(document, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


class SignatureVerifier(Protocol):
    def verify(self, message: bytes, signature_hex: str) -> bool:
        """Verify a signature without exposing signing capability to the caller."""


class NonceStore(Protocol):
    def consume(self, nonce: str, expires_at: datetime, now: datetime) -> bool:
        """Atomically consume a nonce once; production must be durable."""


class HmacSha256TestVerifier:
    """Test-only adapter. Never use as a production trust/key-custody decision."""

    def __init__(self, key: bytes):
        require(isinstance(key, bytes) and len(key) >= 32, "APPROVAL_KEY_INVALID")
        self._key = key

    def verify(self, message: bytes, signature_hex: str) -> bool:
        if not isinstance(signature_hex, str) or not re.fullmatch(r"[0-9a-f]{64}", signature_hex):
            return False
        expected = hmac.new(self._key, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature_hex)


class InMemoryNonceStore:
    """Test-only nonce store. It is not crash-safe and must not back production."""

    def __init__(self):
        self._seen: dict[str, datetime] = {}
        self._lock = Lock()

    def consume(self, nonce: str, expires_at: datetime, now: datetime) -> bool:
        with self._lock:
            self._seen = {key: expiry for key, expiry in self._seen.items() if expiry > now}
            if nonce in self._seen:
                return False
            self._seen[nonce] = expires_at
            return True


def verify_approval(
    envelope: ApprovalEnvelope,
    signature_hex: str,
    verifier: SignatureVerifier,
    nonce_store: NonceStore,
    request: AccessRequest,
) -> None:
    """Raise SecurityError unless the approval is valid and its nonce is consumed."""
    require(isinstance(envelope, ApprovalEnvelope), "APPROVAL_REQUIRED")
    for value in (envelope.approval_id, envelope.actor_id, envelope.approver_id,
                  envelope.action, envelope.target_id, envelope.tenant_id):
        require_id(value, "APPROVAL_FIELD_INVALID")
    require(envelope.approver_kind == "human", "APPROVER_MUST_BE_HUMAN")
    require(envelope.approver_id != envelope.actor_id, "SELF_APPROVAL_FORBIDDEN")
    require(envelope.actor_id == request.actor.principal_id, "APPROVAL_ACTOR_MISMATCH")
    require(envelope.action == request.action, "APPROVAL_ACTION_MISMATCH")
    require(envelope.target_id == request.target_id, "APPROVAL_TARGET_MISMATCH")
    require(envelope.tenant_id == request.tenant_id, "APPROVAL_TENANT_MISMATCH")
    require_hash(envelope.payload_sha256)
    require_hash(envelope.policy_sha256)
    require(envelope.payload_sha256 == request.payload_sha256, "APPROVAL_PAYLOAD_MISMATCH")
    require(envelope.policy_sha256 == request.policy_sha256, "APPROVAL_POLICY_MISMATCH")
    require(bool(envelope.evidence_refs), "APPROVAL_EVIDENCE_REQUIRED")
    require(len(set(envelope.evidence_refs)) == len(envelope.evidence_refs),
            "APPROVAL_EVIDENCE_DUPLICATE")
    for reference in envelope.evidence_refs:
        require_id(reference, "APPROVAL_EVIDENCE_INVALID")
    require(as_decimal(envelope.max_spend_usd) == 0, "APPROVAL_SPEND_FORBIDDEN")
    require(envelope.nonce and bool(NONCE.fullmatch(envelope.nonce)), "APPROVAL_NONCE_INVALID")
    require_utc(envelope.issued_at)
    require_utc(envelope.expires_at)
    require_utc(request.now)
    require(envelope.issued_at <= request.now < envelope.expires_at,
            "APPROVAL_EXPIRED_OR_NOT_YET_VALID")
    require(verifier.verify(canonical_approval_bytes(envelope), signature_hex),
            "APPROVAL_SIGNATURE_INVALID")
    require(nonce_store.consume(envelope.nonce, envelope.expires_at, request.now),
            "APPROVAL_REPLAY")
