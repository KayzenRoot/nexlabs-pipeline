"""Versioned SQLite schema migrations for the offline workflow ledger."""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
import sqlite3

from .contracts import CLASSIFICATIONS, RISK_LEVELS, load_workflows

SCHEMA_VERSION = 6

MIGRATION_1 = """
CREATE TABLE IF NOT EXISTS schema_migrations (
  version INTEGER PRIMARY KEY,
  applied_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  event_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  run_id TEXT,
  event_sha256 TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  event_type TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  payload_ref TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  received_at TEXT NOT NULL,
  body_json TEXT NOT NULL,
  PRIMARY KEY (event_id, tenant_id),
  UNIQUE (idempotency_key, tenant_id),
  UNIQUE (event_sha256, tenant_id)
);
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  workflow_id TEXT NOT NULL,
  workflow_version TEXT NOT NULL,
  event_id TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  state TEXT NOT NULL,
  revision INTEGER NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  lease_owner TEXT,
  lease_expires_at TEXT,
  lease_epoch INTEGER NOT NULL DEFAULT 0,
  approval_id TEXT,
  source_lock_sha256 TEXT NOT NULL,
  deadline_at TEXT NOT NULL,
  stale INTEGER NOT NULL DEFAULT 0,
  revoked INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (run_id, tenant_id),
  UNIQUE (run_id, tenant_id),
  FOREIGN KEY (event_id, tenant_id) REFERENCES events(event_id, tenant_id)
);
CREATE TABLE IF NOT EXISTS transitions (
  transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  from_state TEXT,
  to_state TEXT NOT NULL,
  event_id TEXT,
  revision INTEGER NOT NULL,
  reconciliation_ref TEXT,
  occurred_at TEXT NOT NULL,
  FOREIGN KEY (run_id, tenant_id) REFERENCES runs(run_id, tenant_id),
  FOREIGN KEY (event_id, tenant_id) REFERENCES events(event_id, tenant_id)
);
CREATE TABLE IF NOT EXISTS approvals (
  approval_id TEXT NOT NULL,
  run_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  approver_id TEXT NOT NULL,
  action TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  policy_sha256 TEXT NOT NULL,
  nonce TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  result TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (approval_id, run_id, tenant_id),
  FOREIGN KEY (run_id, tenant_id) REFERENCES runs(run_id, tenant_id)
);
CREATE TABLE IF NOT EXISTS nonces (
  nonce TEXT PRIMARY KEY,
  run_id TEXT,
  tenant_id TEXT,
  approval_id TEXT,
  expires_at TEXT NOT NULL,
  consumed_at TEXT NOT NULL,
  retention_until TEXT NOT NULL,
  result TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outbox (
  outbox_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  event_id TEXT NOT NULL,
  payload_ref TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (run_id, tenant_id, event_id),
  FOREIGN KEY (run_id, tenant_id) REFERENCES runs(run_id, tenant_id),
  FOREIGN KEY (event_id, tenant_id) REFERENCES events(event_id, tenant_id)
);
CREATE TABLE IF NOT EXISTS dlq (
  dlq_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  sanitized_ref TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id, tenant_id) REFERENCES runs(run_id, tenant_id)
);
CREATE TRIGGER IF NOT EXISTS events_no_update
BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'IMMUTABLE_EVENT'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete
BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'IMMUTABLE_EVENT'); END;
"""

MIGRATION_2 = """
CREATE INDEX IF NOT EXISTS idx_runs_tenant_state ON runs(tenant_id, state);
CREATE INDEX IF NOT EXISTS idx_transitions_run ON transitions(run_id, tenant_id, revision);
CREATE INDEX IF NOT EXISTS idx_outbox_pending ON outbox(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_nonce_retention ON nonces(retention_until);
"""

APPROVALS_V3_TABLE = """
CREATE TABLE approvals_v3 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  approval_id TEXT NOT NULL,
  run_id TEXT,
  tenant_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  approver_id TEXT NOT NULL,
  approver_role TEXT NOT NULL,
  action TEXT NOT NULL,
  target_id TEXT NOT NULL,
  project_id TEXT NOT NULL,
  task_id TEXT NOT NULL,
  workflow_id TEXT NOT NULL,
  risk TEXT NOT NULL,
  payload_sha256 TEXT NOT NULL,
  policy_sha256 TEXT NOT NULL,
  policy_epoch INTEGER NOT NULL,
  nonce TEXT NOT NULL,
  evidence_refs_json TEXT NOT NULL,
  max_spend_usd TEXT NOT NULL,
  issued_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  result TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE (approval_id, run_id, tenant_id),
  FOREIGN KEY (run_id, tenant_id) REFERENCES runs(run_id, tenant_id)
)
"""

APPROVALS_V3_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_approvals_run ON approvals(run_id, tenant_id)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_approvals_null_run "
    "ON approvals(approval_id) WHERE run_id IS NULL",
)


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}


def _migrate_v3(conn: sqlite3.Connection) -> None:
    tables = _tables(conn)
    if "approvals" not in tables:
        if "approvals_v3" not in tables:
            raise sqlite3.OperationalError("approvals table unavailable")
        columns = _columns(conn, "approvals_v3")
        if not {"approval_id", "tenant_id", "approver_role",
                "evidence_refs_json"}.issubset(columns):
            raise sqlite3.OperationalError("partial approvals_v3 cannot be recovered")
        conn.execute("ALTER TABLE approvals_v3 RENAME TO approvals")
        for statement in APPROVALS_V3_INDEXES:
            conn.execute(statement)
        return
    columns = _columns(conn, "approvals")
    conn.execute("DROP TABLE IF EXISTS approvals_v3")
    if {"approver_role", "evidence_refs_json"}.issubset(columns):
        for statement in APPROVALS_V3_INDEXES:
            conn.execute(statement)
        return
    conn.execute(APPROVALS_V3_TABLE)
    conn.execute(
        "INSERT INTO approvals_v3("
        "approval_id,run_id,tenant_id,actor_id,approver_id,approver_role,action,"
        "target_id,project_id,task_id,workflow_id,risk,payload_sha256,policy_sha256,"
        "policy_epoch,nonce,evidence_refs_json,max_spend_usd,issued_at,expires_at,"
        "result,created_at) "
        "SELECT approval_id,run_id,tenant_id,'LEGACY-ACTOR',approver_id,'OWNER',"
        "action,run_id,'LEGACY-PROJECT','LEGACY-TASK','LEGACY-WORKFLOW','STANDARD',"
        "payload_sha256,policy_sha256,1,nonce,'[\"LEGACY-EVIDENCE\"]','0',"
        "created_at,expires_at,result,created_at FROM approvals"
    )
    conn.execute("DROP TABLE approvals")
    conn.execute("ALTER TABLE approvals_v3 RENAME TO approvals")
    for statement in APPROVALS_V3_INDEXES:
        conn.execute(statement)


def _event_risk(conn: sqlite3.Connection, event_id: str, tenant_id: str) -> str:
    row = conn.execute(
        "SELECT body_json FROM events WHERE event_id=? AND tenant_id=?",
        (event_id, tenant_id),
    ).fetchone()
    if row is None:
        return "HIGH_ASSURANCE"
    try:
        risk = json.loads(row[0]).get("risk")
    except (TypeError, ValueError, AttributeError):
        return "HIGH_ASSURANCE"
    return risk if isinstance(risk, str) and risk in RISK_LEVELS else "HIGH_ASSURANCE"


def _migrate_v4(conn: sqlite3.Connection) -> None:
    if "risk" not in _columns(conn, "runs"):
        conn.execute("ALTER TABLE runs ADD COLUMN risk TEXT NOT NULL DEFAULT 'STANDARD'")
    rows = conn.execute("SELECT run_id,tenant_id,event_id,risk FROM runs").fetchall()
    for run_id, tenant_id, event_id, current in rows:
        if not isinstance(current, str) or current not in RISK_LEVELS:
            conn.execute(
                "UPDATE runs SET risk='HIGH_ASSURANCE' WHERE run_id=? AND tenant_id=?",
                (run_id, tenant_id),
            )
            continue
        event_risk = _event_risk(conn, event_id, tenant_id)
        if RISK_LEVELS[event_risk] > RISK_LEVELS[current]:
            conn.execute(
                "UPDATE runs SET risk=? WHERE run_id=? AND tenant_id=?",
                (event_risk, run_id, tenant_id),
            )


TEXT_NOT_NULL_EMPTY = "TEXT NOT NULL DEFAULT ''"
RUN_V5_COLUMNS = (
    ("idempotency_key", TEXT_NOT_NULL_EMPTY),
    ("agent_id", TEXT_NOT_NULL_EMPTY),
    ("skill_lock_id", "TEXT"),
    ("skill_lock_version", "TEXT"),
    ("skill_lock_hash", "TEXT"),
    ("model_id", "TEXT"),
    ("quota", "INTEGER NOT NULL DEFAULT 0"),
    ("data_classification", "TEXT NOT NULL DEFAULT 'INTERNAL'"),
    ("inputs_ref", TEXT_NOT_NULL_EMPTY),
    ("output_ref", "TEXT"),
    ("evidence_ref", "TEXT"),
    ("approval_ref", "TEXT"),
    ("status", "TEXT NOT NULL DEFAULT 'RECEIVED'"),
    ("gate", "TEXT NOT NULL DEFAULT 'INTERNAL_ONLY'"),
    ("activation", "TEXT NOT NULL DEFAULT 'DISABLED'"),
)

AUDIT_TABLE = """
CREATE TABLE IF NOT EXISTS audit_events (
  audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  tenant_id TEXT NOT NULL,
  actor_id TEXT NOT NULL DEFAULT 'system',
  action TEXT NOT NULL,
  revision INTEGER NOT NULL,
  detail_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id, tenant_id) REFERENCES runs(run_id, tenant_id)
)
"""


def _event_payload(conn: sqlite3.Connection, event_id: str, tenant_id: str) -> dict:
    row = conn.execute(
        "SELECT body_json FROM events WHERE event_id=? AND tenant_id=?",
        (event_id, tenant_id),
    ).fetchone()
    if row is None:
        return {}
    try:
        value = json.loads(row[0])
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _migrate_v5(conn: sqlite3.Connection) -> None:
    columns = _columns(conn, "runs")
    for name, definition in RUN_V5_COLUMNS:
        if name not in columns:
            conn.execute(f"ALTER TABLE runs ADD COLUMN {name} {definition}")
    conn.execute(AUDIT_TABLE)
    if "actor_id" not in _columns(conn, "audit_events"):
        conn.execute(
            "ALTER TABLE audit_events ADD COLUMN actor_id TEXT NOT NULL DEFAULT 'system'"
        )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_run ON audit_events(run_id, tenant_id)"
    )
    workflows = load_workflows()
    rows = conn.execute(
        "SELECT run_id,tenant_id,workflow_id,event_id,state,approval_id,"
        "idempotency_key,agent_id,data_classification,inputs_ref FROM runs"
    ).fetchall()
    for row in rows:
        payload = _event_payload(conn, row["event_id"], row["tenant_id"])
        workflow = workflows.get(row["workflow_id"], {})
        idempotency_key = payload.get("idempotency_key") or row["idempotency_key"] \
            or f"legacy-{row['run_id']}"
        agent_id = payload.get("producer") or row["agent_id"] or "legacy-agent"
        classification = payload.get("data_classification") \
            if payload.get("data_classification") in CLASSIFICATIONS else None
        classification = classification or row["data_classification"] or "INTERNAL"
        inputs_ref = payload.get("payload_ref") or row["inputs_ref"] or "legacy-input"
        gate = workflow.get("gate") if workflow.get("gate") else "HUMAN_APPROVAL_REQUIRED"
        conn.execute(
            "UPDATE runs SET idempotency_key=?,agent_id=?,data_classification=?,"
            "inputs_ref=?,status=?,gate=?,activation='DISABLED',approval_ref=? "
            "WHERE run_id=? AND tenant_id=?",
            (idempotency_key, agent_id, classification, inputs_ref, row["state"],
             gate, row["approval_id"], row["run_id"], row["tenant_id"]),
        )


def _migrate_v6(conn: sqlite3.Connection) -> None:
    audit_columns = _columns(conn, "audit_events")
    if "actor_id" not in audit_columns:
        conn.execute(
            "ALTER TABLE audit_events ADD COLUMN actor_id TEXT NOT NULL DEFAULT 'system'"
        )
    transition_columns = _columns(conn, "transitions")
    if "actor_id" not in transition_columns:
        conn.execute(
            "ALTER TABLE transitions ADD COLUMN actor_id TEXT NOT NULL DEFAULT 'system'"
        )
    if "action" not in transition_columns:
        conn.execute(
            "ALTER TABLE transitions ADD COLUMN action TEXT NOT NULL DEFAULT 'LEGACY'"
        )


MIGRATIONS = {1: MIGRATION_1, 2: MIGRATION_2, 3: _migrate_v3, 4: _migrate_v4,
              5: _migrate_v5, 6: _migrate_v6}


@contextmanager
def _migration_lock(conn: sqlite3.Connection):
    row = conn.execute("PRAGMA database_list").fetchone()
    path = row[2] if row else ""
    if not path:
        yield
        return
    lock_path = path + ".migration.lock"
    handle = open(lock_path, "a+b")
    try:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def apply_migrations(conn: sqlite3.Connection) -> int:
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        current = conn.execute(
            "SELECT COALESCE(MAX(version),0) FROM schema_migrations"
        ).fetchone()[0]
    except sqlite3.OperationalError:
        current = 0
    if current >= SCHEMA_VERSION:
        conn.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
        return current
    with _migration_lock(conn):
        return _apply_migrations_locked(conn)


def _apply_migrations_locked(conn: sqlite3.Connection) -> int:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations "
        "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
    )
    current = conn.execute("SELECT COALESCE(MAX(version),0) FROM schema_migrations").fetchone()[0]
    for version in sorted(MIGRATIONS):
        if version <= current:
            continue
        migration = MIGRATIONS[version]
        if callable(migration):
            conn.execute("BEGIN IMMEDIATE")
            try:
                migration(conn)
                conn.execute(
                    "INSERT INTO schema_migrations(version, applied_at) "
                    "VALUES(?, datetime('now'))",
                    (version,),
                )
                conn.execute("COMMIT")
            except BaseException:
                conn.execute("ROLLBACK")
                raise
        else:
            conn.executescript(migration)
            conn.execute(
                "INSERT INTO schema_migrations(version, applied_at) "
                "VALUES(?, datetime('now'))",
                (version,),
            )
        current = version
    conn.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
    return current
