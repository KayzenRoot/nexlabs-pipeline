"""Immutable, technology-neutral security contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import re

IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
RISKS = frozenset({"LOW", "STANDARD", "ELEVATED", "HIGH_ASSURANCE"})
KINDS = frozenset({"human", "agent", "service"})


class SecurityError(ValueError):
    """A fail-closed security contract violation."""


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise SecurityError(reason)


def require_id(value: str, reason: str = "INVALID_IDENTIFIER") -> None:
    require(isinstance(value, str) and bool(IDENTIFIER.fullmatch(value)), reason)
    require(value != "*", reason)


def require_hash(value: str, reason: str = "INVALID_SHA256") -> None:
    require(isinstance(value, str) and bool(SHA256.fullmatch(value)), reason)


def require_utc(value: datetime, reason: str = "INVALID_TIMESTAMP") -> None:
    require(isinstance(value, datetime) and value.tzinfo is not None
            and value.utcoffset() is not None and value.utcoffset().total_seconds() == 0,
            reason)


def as_decimal(value: Decimal | str | int) -> Decimal:
    require(not isinstance(value, bool), "INVALID_MONEY")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except Exception as exc:
        raise SecurityError("INVALID_MONEY") from exc
    require(result.is_finite() and result >= 0, "INVALID_MONEY")
    return result


@dataclass(frozen=True)
class Principal:
    principal_id: str
    kind: str
    tenant_id: str
    project_id: str
    host_id: str
    state: str
    policy_epoch: int


@dataclass(frozen=True)
class Grant:
    grant_id: str
    principal_id: str
    action: str
    target_id: str
    tenant_id: str
    project_id: str
    task_id: str
    workflow_id: str
    skill_id: str
    host_id: str
    provider_id: str
    risk: str
    policy_sha256: str
    policy_epoch: int
    issued_at: datetime
    expires_at: datetime
    revoked: bool = False
    max_spend_usd: Decimal = Decimal("0")
    external_effects: str = "DENY"


@dataclass(frozen=True)
class ApprovalEnvelope:
    approval_id: str
    actor_id: str
    approver_id: str
    approver_kind: str
    action: str
    target_id: str
    tenant_id: str
    payload_sha256: str
    policy_sha256: str
    evidence_refs: tuple[str, ...]
    max_spend_usd: Decimal
    nonce: str
    issued_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class AccessRequest:
    actor: Principal
    action: str
    target_id: str
    tenant_id: str
    project_id: str
    task_id: str
    workflow_id: str
    skill_id: str
    host_id: str
    provider_id: str
    risk: str
    policy_sha256: str
    policy_epoch: int
    payload_sha256: str
    effect: str
    requested_spend_usd: Decimal
    now: datetime


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    reason: str
    grant_id: str | None = None
