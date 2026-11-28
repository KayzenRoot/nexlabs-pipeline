"""Small fail-closed validator for the versioned workflow JSON schemas."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re

from security.contracts import SecurityError


class SchemaValidationError(SecurityError):
    """A produced document does not satisfy its versioned schema."""


def _fail(path: str, reason: str) -> None:
    raise SchemaValidationError(f"{path}: {reason}")


def _type_matches(value, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _validate(value, schema: dict, path: str) -> None:
    if "const" in schema and value != schema["const"]:
        _fail(path, "const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        _fail(path, "enum mismatch")
    expected = schema.get("type")
    if expected is not None:
        allowed = expected if isinstance(expected, list) else [expected]
        if not any(_type_matches(value, item) for item in allowed):
            _fail(path, f"expected {allowed}")
    if isinstance(value, str) and "pattern" in schema:
        if re.fullmatch(schema["pattern"], value) is None:
            _fail(path, "pattern mismatch")
    if isinstance(value, str) and schema.get("format") == "date-time":
        try:
            datetime.fromisoformat(value)
        except ValueError:
            _fail(path, "date-time invalid")
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            _fail(path, "minimum violated")
    if isinstance(value, dict):
        required = schema.get("required", [])
        for name in required:
            if name not in value:
                _fail(path, f"missing {name}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = set(value) - set(properties)
            if unknown:
                _fail(path, f"unknown fields {sorted(unknown)}")
        for name, item in value.items():
            if name in properties:
                _validate(item, properties[name], f"{path}.{name}")
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            _validate(item, schema["items"], f"{path}[{index}]")


def validate_document(document, schema_path: str | Path) -> None:
    try:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SchemaValidationError("SCHEMA_UNAVAILABLE") from exc
    _validate(document, schema, "$")
