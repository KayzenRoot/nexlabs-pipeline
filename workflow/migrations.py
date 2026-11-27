"""Versioned SQLite schema migrations for the offline workflow ledger."""
from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 3

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

MIGRATION_3 = """
CREATE TABLE approvals_v3 (
  approval_id TEXT NOT NULL PRIMARY KEY,
  run_id TEXT,
  tenant_id TEXT NOT NULL,
  actor_id TEXT NOT NULL,
  approver_id TEXT NOT NULL,
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
  expires_at TEXT NOT NULL,
  result TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (run_id, tenant_id) REFERENCES runs(run_id, tenant_id)
);
INSERT INTO approvals_v3(
  approval_id,run_id,tenant_id,actor_id,approver_id,action,target_id,
  project_id,task_id,workflow_id,risk,payload_sha256,policy_sha256,
  policy_epoch,nonce,expires_at,result,created_at)
SELECT approval_id,run_id,tenant_id,'LEGACY-ACTOR',approver_id,action,run_id,
  'LEGACY-PROJECT','LEGACY-TASK','LEGACY-WORKFLOW','STANDARD',payload_sha256,
  policy_sha256,1,nonce,expires_at,result,created_at FROM approvals;
DROP TABLE approvals;
ALTER TABLE approvals_v3 RENAME TO approvals;
CREATE INDEX IF NOT EXISTS idx_approvals_run ON approvals(run_id, tenant_id);
"""

MIGRATIONS = {1: MIGRATION_1, 2: MIGRATION_2, 3: MIGRATION_3}


def apply_migrations(conn: sqlite3.Connection) -> int:
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations "
        "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
    )
    current = conn.execute("SELECT COALESCE(MAX(version),0) FROM schema_migrations").fetchone()[0]
    for version in sorted(MIGRATIONS):
        if version <= current:
            continue
        conn.executescript(MIGRATIONS[version])
        conn.execute(
            "INSERT INTO schema_migrations(version, applied_at) VALUES(?, datetime('now'))",
            (version,),
        )
        current = version
    conn.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
    return current
