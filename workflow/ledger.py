"""Durable, append-only SQLite workflow ledger for the offline WF contract."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from typing import Iterator

from security.contracts import require, require_id, require_utc

from .contracts import (
    WorkflowEvent, assert_transition, canonical_bytes, validate_event, WorkflowError,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT PRIMARY KEY,
  event_sha256 TEXT NOT NULL UNIQUE,
  idempotency_key TEXT NOT NULL UNIQUE,
  tenant_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  received_at TEXT NOT NULL,
  body_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL,
  version TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  event_id TEXT NOT NULL REFERENCES events(event_id),
  state TEXT NOT NULL,
  revision INTEGER NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  lease_owner TEXT,
  lease_expires_at TEXT,
  lease_epoch INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS transitions (
  transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL REFERENCES runs(run_id),
  from_state TEXT,
  to_state TEXT NOT NULL,
  event_id TEXT,
  revision INTEGER NOT NULL,
  occurred_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS nonces (
  nonce TEXT PRIMARY KEY,
  expires_at TEXT NOT NULL,
  consumed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
  outbox_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL REFERENCES runs(run_id),
  event_id TEXT NOT NULL REFERENCES events(event_id),
  payload_ref TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(run_id, event_id)
);
CREATE TABLE IF NOT EXISTS dlq (
  dlq_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  sanitized_ref TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS events_no_update
BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'IMMUTABLE_EVENT'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete
BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'IMMUTABLE_EVENT'); END;
"""


class Ledger:
    """A small durable ledger; all writes are explicit transactions."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path, timeout=30, isolation_level=None,
                                    check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.journal_mode_error = None
        self.conn.execute("PRAGMA busy_timeout=30000")
        try:
            self.conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError as exc:
            # A concurrent initializer may hold the journal-mode lock briefly.
            self.journal_mode_error = str(exc)
        self.conn.execute("PRAGMA synchronous=FULL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA busy_timeout=30000")
        self.conn.executescript(SCHEMA)

    def __enter__(self) -> "Ledger":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.conn.execute("COMMIT")
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise

    @staticmethod
    def _timestamp(value: datetime) -> str:
        require_utc(value)
        return value.isoformat()

    def _insert_event(self, event: WorkflowEvent) -> None:
        validate_event(event)
        try:
            self.conn.execute(
                "INSERT INTO events(event_id,event_sha256,idempotency_key,tenant_id,"
                "event_type,correlation_id,payload_sha256,received_at,body_json) "
                "VALUES(?,?,?,?,?,?,?,?,?)",
                (event.event_id, event.digest(), event.idempotency_key, event.tenant_id,
                 event.event_type, event.correlation_id, event.payload_sha256,
                 self._timestamp(event.received_at),
                 canonical_bytes(event.canonical()).decode("utf-8")),
            )
        except sqlite3.IntegrityError as exc:
            raise WorkflowError("DUPLICATE_EVENT") from exc

    def append_event(self, event: WorkflowEvent) -> None:
        with self._transaction():
            self._insert_event(event)

    def create_run(self, run_id: str, workflow_id: str, version: str,
                   event: WorkflowEvent, now: datetime) -> None:
        require_id(run_id, "RUN_ID_INVALID")
        require_id(workflow_id, "WORKFLOW_ID_INVALID")
        require_id(version, "WORKFLOW_VERSION_INVALID")
        require_utc(now)
        with self._transaction():
            self._insert_event(event)
            try:
                self.conn.execute(
                    "INSERT INTO runs(run_id,workflow_id,version,tenant_id,event_id,state,"
                    "revision,attempts,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (run_id, workflow_id, version, event.tenant_id, event.event_id,
                     "RECEIVED", 0, 0, self._timestamp(now), self._timestamp(now)),
                )
            except sqlite3.IntegrityError as exc:
                raise WorkflowError("DUPLICATE_RUN") from exc
            self.conn.execute(
                "INSERT INTO transitions(run_id,from_state,to_state,event_id,revision,occurred_at) "
                "VALUES(?,?,?,?,?,?)",
                (run_id, None, "RECEIVED", event.event_id, 0, self._timestamp(now)),
            )

    def run(self, run_id: str) -> dict:
        row = self.conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        require(row is not None, "RUN_NOT_FOUND")
        return dict(row)

    def transition(self, run_id: str, target: str, event_id: str | None,
                   now: datetime, expected_revision: int | None = None,
                   lease_owner: str | None = None,
                   lease_epoch: int | None = None) -> int:
        require_utc(now)
        with self._transaction():
            current = self.run(run_id)
            if expected_revision is not None:
                require(current["revision"] == expected_revision, "RUN_REVISION_CONFLICT")
            if current["lease_owner"] is not None and lease_owner is None:
                raise WorkflowError("RUN_LEASE_REQUIRED")
            if lease_owner is not None:
                require(current["lease_owner"] == lease_owner, "RUN_LEASE_OWNER_MISMATCH")
                require(current["lease_epoch"] == lease_epoch, "RUN_LEASE_FENCE_MISMATCH")
                require(current["lease_expires_at"] is not None
                        and datetime.fromisoformat(current["lease_expires_at"]) > now,
                        "RUN_LEASE_EXPIRED")
            assert_transition(current["state"], target)
            revision = current["revision"] + 1
            attempts = current["attempts"] + (1 if target == "RETRY_WAIT" else 0)
            self.conn.execute(
                "UPDATE runs SET state=?,revision=?,attempts=?,updated_at=? WHERE run_id=?",
                (target, revision, attempts, self._timestamp(now), run_id),
            )
            self.conn.execute(
                "INSERT INTO transitions(run_id,from_state,to_state,event_id,revision,occurred_at) "
                "VALUES(?,?,?,?,?,?)",
                (run_id, current["state"], target, event_id, revision, self._timestamp(now)),
            )
            return revision

    def claim_lease(self, run_id: str, owner: str, now: datetime,
                    ttl_seconds: int = 30) -> int:
        require_id(owner, "LEASE_OWNER_INVALID")
        require_utc(now)
        require(type(ttl_seconds) is int and 1 <= ttl_seconds <= 3600, "LEASE_TTL_INVALID")
        with self._transaction():
            current = self.run(run_id)
            require(current["state"] == "RUNNING", "LEASE_STATE_INVALID")
            active = (current["lease_owner"] is not None
                      and current["lease_expires_at"] is not None
                      and datetime.fromisoformat(current["lease_expires_at"]) > now)
            require(not active or current["lease_owner"] == owner, "LEASE_HELD")
            epoch = current["lease_epoch"] + 1
            expires = now + timedelta(seconds=ttl_seconds)
            self.conn.execute(
                "UPDATE runs SET lease_owner=?,lease_expires_at=?,lease_epoch=?,updated_at=? "
                "WHERE run_id=?",
                (owner, self._timestamp(expires), epoch, self._timestamp(now), run_id),
            )
            return epoch

    def consume(self, nonce: str, expires_at: datetime, now: datetime) -> bool:
        """NonceStore protocol: atomically consume one durable approval nonce."""
        require_id(nonce, "NONCE_INVALID")
        require_utc(expires_at)
        require_utc(now)
        with self._transaction():
            self.conn.execute("DELETE FROM nonces WHERE expires_at <= ?", (self._timestamp(now),))
            exists = self.conn.execute("SELECT 1 FROM nonces WHERE nonce=?", (nonce,)).fetchone()
            if exists:
                return False
            self.conn.execute(
                "INSERT INTO nonces(nonce,expires_at,consumed_at) VALUES(?,?,?)",
                (nonce, self._timestamp(expires_at), self._timestamp(now)),
            )
            return True

    def enqueue_outbox(self, run_id: str, event_id: str, payload_ref: str,
                       now: datetime) -> None:
        require_utc(now)
        with self._transaction():
            try:
                self.conn.execute(
                    "INSERT INTO outbox(run_id,event_id,payload_ref,status,created_at) "
                    "VALUES(?,?,?,?,?)",
                    (run_id, event_id, payload_ref, "PENDING", self._timestamp(now)),
                )
            except sqlite3.IntegrityError as exc:
                raise WorkflowError("DUPLICATE_OUTBOX") from exc

    def dead_letter(self, run_id: str, reason: str, sanitized_ref: str,
                    now: datetime) -> None:
        require_utc(now)
        require_id(reason, "DLQ_REASON_INVALID")
        require_id(sanitized_ref, "DLQ_REFERENCE_INVALID")
        with self._transaction():
            self.conn.execute(
                "INSERT INTO dlq(run_id,reason,sanitized_ref,created_at) VALUES(?,?,?,?)",
                (run_id, reason, sanitized_ref, self._timestamp(now)),
            )

    def recover(self, now: datetime) -> dict[str, int]:
        """Recover expired work without blind retry; reconcile unknown effects."""
        require_utc(now)
        recovered_retry = 0
        unknown_effect = 0
        with self._transaction():
            rows = self.conn.execute(
                "SELECT * FROM runs WHERE state='RUNNING' AND lease_expires_at IS NOT NULL "
                "AND lease_expires_at <= ?", (self._timestamp(now),),
            ).fetchall()
            for row in rows:
                revision = row["revision"] + 1
                self.conn.execute(
                    "UPDATE runs SET state='RETRY_WAIT',revision=?,updated_at=? WHERE run_id=?",
                    (revision, self._timestamp(now), row["run_id"]),
                )
                self.conn.execute(
                    "INSERT INTO transitions(run_id,from_state,to_state,event_id,revision,occurred_at) "
                    "VALUES(?,?,?,?,?,?)",
                    (row["run_id"], "RUNNING", "RETRY_WAIT", None, revision, self._timestamp(now)),
                )
                recovered_retry += 1
            rows = self.conn.execute(
                "SELECT * FROM runs WHERE state='EFFECT_IN_PROGRESS'"
            ).fetchall()
            for row in rows:
                revision = row["revision"] + 1
                self.conn.execute(
                    "UPDATE runs SET state='UNKNOWN_EFFECT',revision=?,updated_at=? WHERE run_id=?",
                    (revision, self._timestamp(now), row["run_id"]),
                )
                self.conn.execute(
                    "INSERT INTO transitions(run_id,from_state,to_state,event_id,revision,occurred_at) "
                    "VALUES(?,?,?,?,?,?)",
                    (row["run_id"], "EFFECT_IN_PROGRESS", "UNKNOWN_EFFECT", None,
                     revision, self._timestamp(now)),
                )
                unknown_effect += 1
        return {"retry_wait": recovered_retry, "unknown_effect": unknown_effect}

    def integrity(self) -> str:
        result = self.conn.execute("PRAGMA integrity_check").fetchone()[0]
        require(result == "ok", "LEDGER_INTEGRITY_FAILED")
        return result

    def counts(self) -> dict[str, int]:
        tables = ("events", "runs", "transitions", "nonces", "outbox", "dlq")
        return {table: self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in tables}
