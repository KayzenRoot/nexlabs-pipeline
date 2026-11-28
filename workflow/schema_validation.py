"""Small fail-closed validator for the versioned workflow JSON schemas."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re

from security.contracts import SecurityError

SHA256_PATTERN = "^[0-9a-f]{64}$"
_SHA256 = re.compile(SHA256_PATTERN)
SUPPORTED_SCHEMA_KEYS = frozenset({
    "$schema", "$id", "type", "additionalProperties", "required", "properties",
    "enum", "const", "pattern", "format", "minimum", "items", "minItems",
})
SUPPORTED_TYPES = frozenset({
    "object", "array", "string", "integer", "boolean", "null",
})
SUPPORTED_FORMATS = frozenset({"date-time"})


class SchemaValidationError(SecurityError):
    """A produced document does not satisfy its versioned schema."""


def _fail(path: str, reason: str) -> None:
    raise SchemaValidationError(f"{path}: {reason}")


def _type_matches(value, expected: str) -> bool:
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return checks[expected](value)


def _validate_identity(value, schema: dict, path: str) -> None:
    if "const" in schema and value != schema["const"]:
        _fail(path, "const mismatch")
    if "enum" in schema and value not in schema["enum"]:
        _fail(path, "enum mismatch")
    expected = schema.get("type")
    if expected is not None:
        allowed = expected if isinstance(expected, list) else [expected]
        if not allowed or any(item not in SUPPORTED_TYPES for item in allowed):
            _fail(path, "unsupported schema type")
        if not any(_type_matches(value, item) for item in allowed):
            _fail(path, f"expected {allowed}")


def _validate_string(value, schema: dict, path: str) -> None:
    if not isinstance(value, str):
        return
    if "pattern" in schema:
        if schema["pattern"] != SHA256_PATTERN:
            _fail(path, "unsupported schema pattern")
        if _SHA256.fullmatch(value) is None:
            _fail(path, "pattern mismatch")
    if schema.get("format") == "date-time":
        if "T" not in value:
            _fail(path, "date-time missing time")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            _fail(path, "date-time invalid")
        if parsed.tzinfo is None:
            _fail(path, "date-time timezone required")


def _validate_scalar(value, schema: dict, path: str) -> None:
    _validate_identity(value, schema, path)
    _validate_string(value, schema, path)
    if isinstance(value, int) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            _fail(path, "minimum violated")


def _validate_object(value: dict, schema: dict, path: str) -> None:
    for name in schema.get("required", []):
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


def _validate_array(value: list, schema: dict, path: str) -> None:
    if len(value) < schema.get("minItems", 0):
        _fail(path, "minItems violated")
    if "items" in schema:
        for index, item in enumerate(value):
            _validate(item, schema["items"], f"{path}[{index}]")


def _validate(value, schema: dict, path: str) -> None:
    unsupported = set(schema) - SUPPORTED_SCHEMA_KEYS
    if unsupported:
        _fail(path, f"unsupported schema keywords {sorted(unsupported)}")
    if "format" in schema and schema["format"] not in SUPPORTED_FORMATS:
        _fail(path, "unsupported schema format")
    _validate_scalar(value, schema, path)
    if isinstance(value, dict):
        _validate_object(value, schema, path)
    elif isinstance(value, list):
        _validate_array(value, schema, path)


def validate_document(document, schema_path: str | Path) -> None:
    try:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SchemaValidationError("SCHEMA_UNAVAILABLE") from exc
    _validate(document, schema, "$")
