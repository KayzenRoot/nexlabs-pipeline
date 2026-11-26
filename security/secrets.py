"""Opaque, version-pinned secret references. This module never resolves values."""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import require, require_id


@dataclass(frozen=True)
class SecretRef:
    reference_id: str
    provider_id: str
    tenant_id: str
    project_id: str
    purpose: str
    version: str


def validate_secret_ref(
    reference: SecretRef,
    *,
    tenant_id: str,
    project_id: str,
    allowed_providers: frozenset[str],
    allowed_purposes: frozenset[str],
) -> None:
    require(isinstance(reference, SecretRef), "SECRET_REFERENCE_INVALID")
    for value in (
        reference.reference_id, reference.provider_id, reference.tenant_id,
        reference.project_id, reference.purpose, reference.version,
    ):
        require_id(value, "SECRET_REFERENCE_FIELD_INVALID")
    require(reference.provider_id in allowed_providers, "SECRET_PROVIDER_NOT_APPROVED")
    require(reference.purpose in allowed_purposes, "SECRET_PURPOSE_NOT_APPROVED")
    require(reference.tenant_id == tenant_id, "SECRET_TENANT_MISMATCH")
    require(reference.project_id == project_id, "SECRET_PROJECT_MISMATCH")
    require(reference.version.lower() != "latest", "SECRET_VERSION_NOT_PINNED")
