"""Tenant and workspace path isolation checks; never creates or mutates paths."""
from __future__ import annotations

import os
from pathlib import Path, PurePosixPath

from .contracts import SecurityError, require, require_id


def assert_tenant_match(principal_tenant: str, resource_tenant: str) -> None:
    require_id(principal_tenant)
    require_id(resource_tenant)
    require(principal_tenant == resource_tenant, "TENANT_ISOLATION_DENY")


def _is_link_or_reparse(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise SecurityError("WORKSPACE_METADATA_UNAVAILABLE") from exc
    return path.is_symlink() or bool(getattr(metadata, "st_file_attributes", 0) & 0x400)


def resolve_workspace_path(
    root: Path,
    tenant_id: str,
    project_id: str,
    task_id: str,
    relative_path: str,
) -> Path:
    """Return a contained path only; reject links/reparse points and traversal."""
    for value in (tenant_id, project_id, task_id):
        require_id(value, "WORKSPACE_SCOPE_INVALID")
    require(isinstance(relative_path, str) and relative_path
            and "\\" not in relative_path and ":" not in relative_path,
            "WORKSPACE_PATH_INVALID")
    relative = PurePosixPath(relative_path)
    require(not relative.is_absolute() and relative.as_posix() == relative_path
            and ".." not in relative.parts and "." not in relative.parts,
            "WORKSPACE_PATH_INVALID")
    root = Path(root)
    require(root.exists() and root.is_dir() and not _is_link_or_reparse(root),
            "WORKSPACE_ROOT_INVALID")
    root_resolved = root.resolve(strict=True)
    components = (tenant_id, project_id, task_id, *relative.parts)
    candidate = root
    for component in components:
        candidate = candidate / component
        require(not _is_link_or_reparse(candidate), "WORKSPACE_LINK_FORBIDDEN")
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise SecurityError("WORKSPACE_ESCAPE_DENY") from exc
    return resolved
