"""Fail-closed transaction outcome vocabulary for workflow ledger operations."""
from __future__ import annotations

from enum import Enum
import sqlite3


class TxOutcome(str, Enum):
    COMMITTED = "COMMITTED"
    REPLAY_REJECTED = "REPLAY_REJECTED"
    CONFLICT = "CONFLICT"
    STORAGE_ERROR = "STORAGE_ERROR"


def classify_exception(exc: BaseException) -> TxOutcome:
    if isinstance(exc, sqlite3.IntegrityError):
        return TxOutcome.CONFLICT
    if isinstance(exc, sqlite3.Error):
        return TxOutcome.STORAGE_ERROR
    text = str(exc).upper()
    if "REPLAY" in text or "NONCE" in text:
        return TxOutcome.REPLAY_REJECTED
    if any(token in text for token in (
        "CONFLICT", "REVISION", "LEASE", "STATE", "STALE", "REVOKED",
        "DEADLINE", "FENCE", "OWNER",
    )):
        return TxOutcome.CONFLICT
    return TxOutcome.STORAGE_ERROR
