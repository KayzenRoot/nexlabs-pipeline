"""Durable append-only workflow ledger. Mutations are private storage primitives."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import threading
from typing import Iterator

from security.contracts import (
    AccessRequest, ApprovalEnvelope, as_decimal, require, require_hash, require_id,
    require_utc,
)

from .contracts import (
    EXECUTOR_STATES, MAX_ATTEMPTS, OUTBOX_BLOCKED_STATES, RISK_LEVELS, ROOT,
    RunContract, RunOptions, WorkflowEvent, assert_transition, canonical_bytes,
    require_risk_floor, validate_event, WorkflowError,
)
from .migrations import apply_migrations
from .outcomes import TxOutcome
from .schema_validation import validate_document


TRANSITION_INSERT = (
    "INSERT INTO transitions(run_id,tenant_id,from_state,to_state,event_id,"
    "revision,reconciliation_ref,occurred_at,actor_id,action) "
    "VALUES(?,?,?,?,?,?,?,?,?,?)"
)
TRANSITION_INSERT_PLAIN = (
    "INSERT INTO transitions(run_id,tenant_id,from_state,to_state,event_id,"
    "revision,occurred_at,actor_id,action) VALUES(?,?,?,?,?,?,?,?,?)"
)


class Ledger:
    """SQLite storage; public reads only. Commands use the private primitives."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self._conn = sqlite3.connect(self.path, timeout=30, isolation_level=None,
                                     check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA busy_timeout=30000")
        mode = self._conn.execute("PRAGMA journal_mode=WAL").fetchone()[0]
        require(str(mode).lower() == "wal", "LEDGER_WAL_REQUIRED")
        self._conn.execute("PRAGMA synchronous=FULL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        try:
            apply_migrations(self._conn)
        except BaseException:
            self._conn.close()
            raise
        self._tx_depth = 0
        self._tx_owner = None
        self._lock = threading.RLock()

    def __enter__(self) -> "Ledger":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    @property
    def schema_version(self) -> int:
        with self._lock:
            return self._conn.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()[0]

    @contextmanager
    def _transaction(self) -> Iterator[None]:
        owner = threading.get_ident()
        with self._lock:
            if self._tx_depth:
                require(self._tx_owner == owner, "TRANSACTION_OWNER_MISMATCH")
                yield
                return
            self._tx_owner = owner
            self._tx_depth = 1
            try:
                self._conn.execute("BEGIN IMMEDIATE")
                yield
                self._conn.execute("COMMIT")
            except BaseException:
                self._conn.execute("ROLLBACK")
                raise
            finally:
                self._tx_depth = 0
                self._tx_owner = None

    @staticmethod
    def _timestamp(value: datetime) -> str:
        require_utc(value)
        return value.isoformat()

    def _insert_event(self, event: WorkflowEvent, run_id: str | None = None) -> None:
        validate_event(event)
        validate_document(event.canonical(), ROOT / "workflow/schemas/event-v1.json")
        try:
            self._conn.execute(
                "INSERT INTO events(event_id,tenant_id,run_id,event_sha256,idempotency_key,"
                "event_type,correlation_id,payload_ref,payload_sha256,received_at,body_json) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (event.event_id, event.tenant_id, run_id, event.digest(), event.idempotency_key,
                 event.event_type, event.correlation_id, event.payload_ref, event.payload_sha256,
                 self._timestamp(event.received_at), canonical_bytes(event.canonical()).decode()),
            )
        except sqlite3.IntegrityError as exc:
            raise WorkflowError("DUPLICATE_EVENT_OR_IDEMPOTENCY") from exc

    def _append_event(self, event: WorkflowEvent, run_id: str | None = None,
                      *, scope: tuple[str, str, str] | None = None,
                      actor_id: str = "system",
                      action: str = "workflow.event.append",
                      now: datetime | None = None) -> None:
        require(run_id is None or isinstance(run_id, str), "RUN_ID_INVALID")
        with self._transaction():
            run = None
            if run_id is not None:
                run = (self.run_scoped(run_id, event.tenant_id, *scope) if scope
                       else self._conn.execute(
                           "SELECT * FROM runs WHERE run_id=? AND tenant_id=?",
                           (run_id, event.tenant_id),
                       ).fetchone())
                require(run is not None, "EVENT_RUN_TENANT_MISMATCH")
            self._insert_event(event, run_id)
            if run is not None:
                audit_now = now or event.received_at
                require_utc(audit_now)
                self._audit(run_id, event.tenant_id, actor_id, action,
                            run["revision"],
                            {"event_id": event.event_id,
                             "payload_ref": event.payload_ref}, audit_now)

    def _create_run(self, run_id: str, tenant_id: str, project_id: str, task_id: str,
                    workflow_id: str, workflow_version: str, event: WorkflowEvent,
                    now: datetime, deadline_at: datetime, source_lock_sha256: str,
                    options: RunOptions | None = None,
                    actor_id: str = "system") -> None:
        for value in (run_id, project_id, task_id, workflow_id, workflow_version):
            require_id(value, "RUN_IDENTIFIER_INVALID")
        require_utc(now)
        require_utc(deadline_at)
        require(deadline_at > now, "RUN_DEADLINE_INVALID")
        require_hash(source_lock_sha256)
        require(event.tenant_id == tenant_id, "EVENT_TENANT_MISMATCH")
        options = options or RunOptions()
        contract = RunContract(
            run_id=run_id, tenant_id=tenant_id, project_id=project_id, task_id=task_id,
            workflow_id=workflow_id, workflow_version=workflow_version,
            event_id=event.event_id, correlation_id=event.correlation_id, state="RECEIVED",
            revision=0, attempts=0, source_lock_sha256=source_lock_sha256,
            deadline_at=deadline_at, risk=options.risk,
            idempotency_key=event.idempotency_key,
            agent_id=options.agent_id or event.producer,
            skill_lock_id=options.skill_lock_id,
            skill_lock_version=options.skill_lock_version,
            skill_lock_hash=options.skill_lock_hash, model_id=options.model_id,
            quota=options.quota, data_classification=event.data_classification,
            inputs_ref=event.payload_ref, output_ref=options.output_ref,
            evidence_ref=options.evidence_ref, gate=options.gate,
        )
        contract.validate()
        validate_document(contract.document(), ROOT / "workflow/schemas/run-v1.json")
        with self._transaction():
            self._insert_event(event, run_id)
            try:
                self._conn.execute(
                    "INSERT INTO runs(run_id,tenant_id,project_id,task_id,workflow_id,"
                    "workflow_version,event_id,correlation_id,state,status,revision,attempts,"
                    "source_lock_sha256,deadline_at,risk,idempotency_key,agent_id,"
                    "skill_lock_id,skill_lock_version,skill_lock_hash,model_id,quota,"
                    "data_classification,inputs_ref,output_ref,evidence_ref,gate,activation,"
                    "created_at,updated_at) VALUES("
                    "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (run_id, tenant_id, project_id, task_id, workflow_id, workflow_version,
                     event.event_id, event.correlation_id, "RECEIVED", "RECEIVED", 0, 0,
                     source_lock_sha256, self._timestamp(deadline_at), options.risk,
                     contract.idempotency_key, contract.agent_id, contract.skill_lock_id,
                     contract.skill_lock_version, contract.skill_lock_hash, contract.model_id,
                     contract.quota, contract.data_classification, contract.inputs_ref,
                     contract.output_ref, contract.evidence_ref, contract.gate, "DISABLED",
                     self._timestamp(now), self._timestamp(now)),
                )
            except sqlite3.IntegrityError as exc:
                raise WorkflowError("DUPLICATE_RUN_OR_EVENT") from exc
            self._conn.execute(
                TRANSITION_INSERT_PLAIN,
                (run_id, tenant_id, None, "RECEIVED", event.event_id, 0,
                 self._timestamp(now), actor_id, "workflow.run.create"),
            )

    def run(self, run_id: str, tenant_id: str) -> dict:
        require_id(run_id, "RUN_ID_INVALID")
        require_id(tenant_id, "TENANT_ID_INVALID")
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM runs WHERE run_id=? AND tenant_id=?", (run_id, tenant_id)
            ).fetchone()
        require(row is not None, "RUN_NOT_FOUND")
        return dict(row)

    def run_scoped(self, run_id: str, tenant_id: str, project_id: str,
                   task_id: str, workflow_id: str) -> dict:
        require_id(run_id, "RUN_ID_INVALID")
        for value in (tenant_id, project_id, task_id, workflow_id):
            require_id(value, "RUN_SCOPE_INVALID")
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM runs WHERE run_id=? AND tenant_id=? AND project_id=? "
                "AND task_id=? AND workflow_id=?",
                (run_id, tenant_id, project_id, task_id, workflow_id),
            ).fetchone()
        require(row is not None, "RUN_SCOPE_MISMATCH")
        return dict(row)

    def _transition(self, run_id: str, tenant_id: str, target: str, event_id: str | None,
                    now: datetime, expected_revision: int, lease_owner: str | None = None,
                    lease_epoch: int | None = None,
                    reconciliation_ref: str | None = None,
                    *, scope: tuple[str, str, str] | None = None,
                    actor_id: str = "system",
                    action: str = "workflow.run.transition") -> int:
        require_utc(now)
        require(type(expected_revision) is int and expected_revision >= 0,
                "RUN_REVISION_REQUIRED")
        with self._transaction():
            require(target != "QUARANTINED", "QUARANTINE_REQUIRES_DLQ")
            current = (self.run_scoped(run_id, tenant_id, *scope) if scope
                       else self.run(run_id, tenant_id))
            require(current["revision"] == expected_revision, "RUN_REVISION_CONFLICT")
            require(not current["stale"], "RUN_STALE")
            require(not current["revoked"], "RUN_REVOKED")
            require(datetime.fromisoformat(current["deadline_at"]) > now, "RUN_DEADLINE_EXPIRED")
            if current["state"] in EXECUTOR_STATES:
                require(lease_owner is not None and lease_epoch is not None, "RUN_LEASE_REQUIRED")
                require(current["lease_owner"] == lease_owner, "RUN_LEASE_OWNER_MISMATCH")
                require(current["lease_epoch"] == lease_epoch, "RUN_LEASE_FENCE_MISMATCH")
                require(current["lease_expires_at"] is not None
                        and datetime.fromisoformat(current["lease_expires_at"]) > now,
                        "RUN_LEASE_EXPIRED")
            if event_id is not None:
                event = self._conn.execute(
                    "SELECT tenant_id,run_id FROM events WHERE event_id=?", (event_id,)
                ).fetchone()
                require(event is not None, "TRANSITION_EVENT_NOT_FOUND")
                require(event["tenant_id"] == tenant_id, "TRANSITION_EVENT_TENANT_MISMATCH")
                require(event["run_id"] == run_id, "TRANSITION_EVENT_RUN_MISMATCH")
            if current["state"] == "UNKNOWN_EFFECT" and target in {"VERIFIED", "FAILED", "BLOCKED"}:
                require(reconciliation_ref is not None, "RECONCILIATION_EVIDENCE_REQUIRED")
                require_id(reconciliation_ref, "RECONCILIATION_REFERENCE_INVALID")
            if target == "RETRY_WAIT":
                require(current["attempts"] + 1 < MAX_ATTEMPTS, "RETRY_LIMIT_EXCEEDED")
            assert_transition(current["state"], target)
            revision = current["revision"] + 1
            attempts = current["attempts"] + (1 if target == "RETRY_WAIT" else 0)
            self._conn.execute(
                "UPDATE runs SET state=?,status=?,revision=?,attempts=?,lease_owner=NULL,"
                "lease_expires_at=NULL,updated_at=? WHERE run_id=? AND tenant_id=?",
                (target, target, revision, attempts, self._timestamp(now), run_id,
                 tenant_id),
            )
            self._conn.execute(
                TRANSITION_INSERT,
                (run_id, tenant_id, current["state"], target, event_id, revision,
                 reconciliation_ref, self._timestamp(now), actor_id, action),
            )
            return revision

    def _claim_lease(self, run_id: str, tenant_id: str, owner: str, now: datetime,
                     ttl_seconds: int, expected_revision: int,
                     *, scope: tuple[str, str, str] | None = None,
                     actor_id: str = "system") -> int:
        require_id(owner, "LEASE_OWNER_INVALID")
        require_utc(now)
        require(type(ttl_seconds) is int and 1 <= ttl_seconds <= 3600, "LEASE_TTL_INVALID")
        require(type(expected_revision) is int and expected_revision >= 0,
                "RUN_REVISION_REQUIRED")
        with self._transaction():
            current = (self.run_scoped(run_id, tenant_id, *scope) if scope
                       else self.run(run_id, tenant_id))
            require(current["revision"] == expected_revision, "RUN_REVISION_CONFLICT")
            require(current["state"] in {"RUNNING", "EFFECT_IN_PROGRESS"},
                    "LEASE_STATE_INVALID")
            require(not current["stale"] and not current["revoked"], "RUN_NOT_CLAIMABLE")
            require(datetime.fromisoformat(current["deadline_at"]) > now, "RUN_DEADLINE_EXPIRED")
            require(current["attempts"] < MAX_ATTEMPTS, "RETRY_LIMIT_EXCEEDED")
            active = (current["lease_owner"] is not None
                      and datetime.fromisoformat(current["lease_expires_at"]) > now)
            if active:
                require(current["lease_owner"] == owner, "LEASE_HELD")
            elif current["lease_owner"] is not None:
                require(False, "LEASE_EXPIRED_RECOVERY_REQUIRED")
            epoch = current["lease_epoch"] + 1
            self._conn.execute(
                "UPDATE runs SET lease_owner=?,lease_expires_at=?,lease_epoch=?,updated_at=? "
                "WHERE run_id=? AND tenant_id=?",
                (owner, self._timestamp(now + timedelta(seconds=ttl_seconds)), epoch,
                 self._timestamp(now), run_id, tenant_id),
            )
            self._audit(run_id, tenant_id, actor_id, "CLAIM_LEASE",
                        current["revision"],
                        {"owner": owner, "epoch": epoch, "ttl_seconds": ttl_seconds}, now)
            return epoch

    def _audit(self, run_id: str, tenant_id: str, actor_id: str, action: str,
               revision: int, detail: dict, now: datetime) -> None:
        self._conn.execute(
            "INSERT INTO audit_events(run_id,tenant_id,actor_id,action,revision,"
            "detail_json,created_at) VALUES(?,?,?,?,?,?,?)",
            (run_id, tenant_id, actor_id, action, revision,
             canonical_bytes(detail).decode(), self._timestamp(now)),
        )

    def _consume_outcome(self, nonce: str, expires_at: datetime, now: datetime,
                         run_id: str | None = None, tenant_id: str | None = None,
                         approval_id: str | None = None,
                         result: str = "CONSUMED") -> tuple[bool, TxOutcome]:
        require_id(nonce, "NONCE_INVALID")
        require_utc(expires_at)
        require_utc(now)
        require(expires_at > now, "NONCE_EXPIRED")
        require(result in {"CONSUMED", "REJECTED"}, "NONCE_RESULT_INVALID")
        retention = expires_at + timedelta(hours=24)
        try:
            with self._transaction():
                exists = self._conn.execute(
                    "SELECT 1 FROM nonces WHERE nonce=?", (nonce,)
                ).fetchone()
                if exists:
                    return False, TxOutcome.REPLAY_REJECTED
                self._conn.execute(
                    "INSERT INTO nonces(nonce,run_id,tenant_id,approval_id,expires_at,"
                    "consumed_at,retention_until,result) VALUES(?,?,?,?,?,?,?,?)",
                    (nonce, run_id, tenant_id, approval_id, self._timestamp(expires_at),
                     self._timestamp(now), self._timestamp(retention), result),
                )
                return True, TxOutcome.COMMITTED
        except sqlite3.IntegrityError:
            return False, TxOutcome.CONFLICT
        except sqlite3.Error:
            return False, TxOutcome.STORAGE_ERROR

    def _consume(self, nonce: str, expires_at: datetime, now: datetime,
                 run_id: str | None = None, tenant_id: str | None = None,
                 approval_id: str | None = None, result: str = "CONSUMED") -> bool:
        consumed, outcome = self._consume_outcome(
            nonce, expires_at, now, run_id, tenant_id, approval_id, result,
        )
        require(outcome is not TxOutcome.STORAGE_ERROR, "NONCE_STORAGE_ERROR")
        return consumed

    def _record_approval(self, request: AccessRequest, approval: ApprovalEnvelope,
                         run_id: str | None, result: str, now: datetime) -> None:
        require_utc(now)
        require_utc(approval.expires_at)
        if run_id is not None:
            run = self._conn.execute(
                "SELECT 1 FROM runs WHERE run_id=? AND tenant_id=?",
                (run_id, request.tenant_id),
            ).fetchone()
            require(run is not None, "APPROVAL_RUN_NOT_FOUND")
        with self._transaction():
            try:
                self._conn.execute(
                    "INSERT INTO approvals(approval_id,run_id,tenant_id,actor_id,approver_id,"
                    "approver_role,action,target_id,project_id,task_id,workflow_id,risk,"
                    "payload_sha256,policy_sha256,policy_epoch,nonce,evidence_refs_json,"
                    "max_spend_usd,issued_at,expires_at,result,created_at) "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (approval.approval_id, run_id, request.tenant_id,
                     request.actor.principal_id, approval.approver_id,
                     approval.approver_role, request.action, request.target_id,
                     request.project_id, request.task_id, request.workflow_id,
                     request.risk, request.payload_sha256, request.policy_sha256,
                     request.policy_epoch, approval.nonce,
                     canonical_bytes(list(approval.evidence_refs)).decode(),
                     str(as_decimal(approval.max_spend_usd)), approval.issued_at.isoformat(),
                     self._timestamp(approval.expires_at), result, self._timestamp(now)),
                )
                if run_id is not None and request.action == "workflow.run.create":
                    self._conn.execute(
                        "UPDATE runs SET approval_id=?,approval_ref=?,updated_at=? "
                        "WHERE run_id=? AND tenant_id=?",
                        (approval.approval_id, approval.approval_id,
                         self._timestamp(now), run_id, request.tenant_id),
                    )
            except sqlite3.IntegrityError as exc:
                raise WorkflowError("APPROVAL_ALREADY_RECORDED") from exc

    def _enqueue_outbox(self, run_id: str, tenant_id: str, event_id: str,
                        payload_ref: str, now: datetime, expected_revision: int,
                        lease_owner: str | None = None, lease_epoch: int | None = None,
                        *, scope: tuple[str, str, str] | None = None,
                        actor_id: str = "system",
                        action: str = "workflow.outbox.enqueue") -> None:
        require_utc(now)
        require(type(expected_revision) is int and expected_revision >= 0,
                "RUN_REVISION_REQUIRED")
        with self._transaction():
            run = (self.run_scoped(run_id, tenant_id, *scope) if scope
                   else self.run(run_id, tenant_id))
            require(run["revision"] == expected_revision, "RUN_REVISION_CONFLICT")
            require(not run["stale"], "RUN_STALE")
            require(not run["revoked"], "RUN_REVOKED")
            require(datetime.fromisoformat(run["deadline_at"]) > now, "RUN_DEADLINE_EXPIRED")
            require(run["state"] not in OUTBOX_BLOCKED_STATES, "OUTBOX_RUN_TERMINAL")
            if run["state"] in EXECUTOR_STATES:
                require(lease_owner is not None and lease_epoch is not None,
                        "RUN_LEASE_REQUIRED")
                require(run["lease_owner"] == lease_owner, "RUN_LEASE_OWNER_MISMATCH")
                require(run["lease_epoch"] == lease_epoch, "RUN_LEASE_FENCE_MISMATCH")
                require(run["lease_expires_at"] is not None
                        and datetime.fromisoformat(run["lease_expires_at"]) > now,
                        "RUN_LEASE_EXPIRED")
            event = self._conn.execute(
                "SELECT tenant_id,run_id,payload_ref FROM events WHERE event_id=?", (event_id,)
            ).fetchone()
            require(event is not None, "OUTBOX_EVENT_NOT_FOUND")
            require(event["tenant_id"] == tenant_id, "OUTBOX_TENANT_MISMATCH")
            require(event["run_id"] == run_id, "OUTBOX_RUN_MISMATCH")
            require(event["payload_ref"] == payload_ref, "OUTBOX_PAYLOAD_REF_MISMATCH")
            try:
                self._conn.execute(
                    "INSERT INTO outbox(run_id,tenant_id,event_id,payload_ref,status,created_at) "
                    "VALUES(?,?,?,?,?,?)",
                    (run_id, tenant_id, event_id, payload_ref, "PENDING", self._timestamp(now)),
                )
            except sqlite3.IntegrityError as exc:
                raise WorkflowError("DUPLICATE_OUTBOX") from exc
            self._audit(run_id, tenant_id, actor_id, action, run["revision"],
                        {"event_id": event_id, "payload_ref": payload_ref}, now)

    def _dead_letter(self, run_id: str, tenant_id: str, reason: str,
                     sanitized_ref: str, now: datetime, expected_revision: int,
                     *, scope: tuple[str, str, str] | None = None,
                     actor_id: str = "system",
                     action: str = "workflow.dlq.record") -> None:
        require_utc(now)
        require_id(reason, "DLQ_REASON_INVALID")
        require_id(sanitized_ref, "DLQ_REFERENCE_INVALID")
        require(not sanitized_ref.startswith(("http:", "https:", "file:")),
                "DLQ_REFERENCE_UNSANITIZED")
        require(type(expected_revision) is int and expected_revision >= 0,
                "RUN_REVISION_REQUIRED")
        with self._transaction():
            run = (self.run_scoped(run_id, tenant_id, *scope) if scope
                   else self.run(run_id, tenant_id))
            require(run["revision"] == expected_revision, "RUN_REVISION_CONFLICT")
            assert_transition(run["state"], "QUARANTINED")
            revision = run["revision"] + 1
            self._conn.execute(
                "UPDATE runs SET state='QUARANTINED',status='QUARANTINED',revision=?,"
                "lease_owner=NULL,lease_expires_at=NULL,updated_at=? "
                "WHERE run_id=? AND tenant_id=?",
                (revision, self._timestamp(now), run_id, tenant_id),
            )
            self._conn.execute(
                TRANSITION_INSERT_PLAIN,
                (run_id, tenant_id, run["state"], "QUARANTINED", None, revision,
                 self._timestamp(now), actor_id, action),
            )
            self._conn.execute(
                "INSERT INTO dlq(run_id,tenant_id,reason,sanitized_ref,created_at) "
                "VALUES(?,?,?,?,?)",
                (run_id, tenant_id, reason, sanitized_ref, self._timestamp(now)),
            )
            self._audit(run_id, tenant_id, actor_id, action, revision,
                        {"reason": reason, "sanitized_ref": sanitized_ref}, now)

    def _recover(self, tenant_id: str, project_id: str, task_id: str,
                 workflow_id: str, now: datetime,
                 risk: str = "HIGH_ASSURANCE",
                 actor_id: str = "system") -> dict[str, int]:
        for value in (tenant_id, project_id, task_id, workflow_id):
            require_id(value, "RECOVERY_SCOPE_INVALID")
        require_utc(now)
        require(risk in RISK_LEVELS, "RECOVERY_RISK_INVALID")
        retry = unknown = failed = 0
        with self._transaction():
            rows = self._conn.execute(
                "SELECT * FROM runs WHERE tenant_id=? AND project_id=? AND task_id=? "
                "AND workflow_id=? AND state='RUNNING' AND "
                "(lease_expires_at IS NULL OR lease_expires_at <= ?)",
                (tenant_id, project_id, task_id, workflow_id, self._timestamp(now)),
            ).fetchall()
            for row in rows:
                require_risk_floor(risk, row["risk"])
                attempts = min(row["attempts"] + 1, MAX_ATTEMPTS)
                terminal = (row["stale"] or row["revoked"]
                            or datetime.fromisoformat(row["deadline_at"]) <= now
                            or attempts >= MAX_ATTEMPTS)
                target = "FAILED" if terminal else "RETRY_WAIT"
                revision = row["revision"] + 1
                self._conn.execute(
                    "UPDATE runs SET state=?,status=?,revision=?,attempts=?,lease_owner=NULL,"
                    "lease_expires_at=NULL,updated_at=? WHERE run_id=? AND tenant_id=?",
                    (target, target, revision, attempts, self._timestamp(now),
                     row["run_id"], tenant_id),
                )
                self._conn.execute(
                    TRANSITION_INSERT_PLAIN,
                    (row["run_id"], tenant_id, "RUNNING", target, None, revision,
                     self._timestamp(now), actor_id, "workflow.recovery.run"),
                )
                if target == "RETRY_WAIT":
                    retry += 1
                else:
                    failed += 1
            rows = self._conn.execute(
                "SELECT * FROM runs WHERE tenant_id=? AND project_id=? AND task_id=? "
                "AND workflow_id=? AND state='EFFECT_IN_PROGRESS' AND "
                "(lease_expires_at IS NULL OR lease_expires_at <= ?)",
                (tenant_id, project_id, task_id, workflow_id, self._timestamp(now)),
            ).fetchall()
            for row in rows:
                require_risk_floor(risk, row["risk"])
                revision = row["revision"] + 1
                self._conn.execute(
                    "UPDATE runs SET state='UNKNOWN_EFFECT',status='UNKNOWN_EFFECT',"
                    "revision=?,lease_owner=NULL,lease_expires_at=NULL,updated_at=? "
                    "WHERE run_id=? AND tenant_id=?",
                    (revision, self._timestamp(now), row["run_id"], tenant_id),
                )
                self._conn.execute(
                    TRANSITION_INSERT_PLAIN,
                    (row["run_id"], tenant_id, "EFFECT_IN_PROGRESS", "UNKNOWN_EFFECT",
                     None, revision, self._timestamp(now), actor_id,
                     "workflow.recovery.run"),
                )
                unknown += 1
        return {"retry_wait": retry, "unknown_effect": unknown, "failed": failed}

    def _set_flags(self, run_id: str, tenant_id: str, now: datetime,
                   stale: bool | None = None, revoked: bool | None = None,
                   expected_revision: int | None = None,
                   *, scope: tuple[str, str, str] | None = None,
                   actor_id: str = "system") -> None:
        require_utc(now)
        require(stale is None or type(stale) is bool, "STALE_FLAG_INVALID")
        require(revoked is None or type(revoked) is bool, "REVOKED_FLAG_INVALID")
        with self._transaction():
            current = (self.run_scoped(run_id, tenant_id, *scope) if scope
                       else self.run(run_id, tenant_id))
            require(type(expected_revision) is int
                    and current["revision"] == expected_revision, "RUN_REVISION_REQUIRED")
            new_stale = current["stale"] if stale is None else int(stale)
            new_revoked = current["revoked"] if revoked is None else int(revoked)
            require(not (current["stale"] and new_stale == 0), "STALE_REVERSAL_FORBIDDEN")
            require(not (current["revoked"] and new_revoked == 0),
                    "REVOCATION_REVERSAL_FORBIDDEN")
            revision = current["revision"] + 1
            self._conn.execute(
                "UPDATE runs SET stale=?,revoked=?,revision=?,updated_at=? "
                "WHERE run_id=? AND tenant_id=?",
                (new_stale, new_revoked, revision, self._timestamp(now), run_id, tenant_id),
            )
            self._audit(run_id, tenant_id, actor_id, "SET_FLAGS", revision,
                        {"stale": bool(new_stale), "revoked": bool(new_revoked)}, now)

    def integrity(self) -> str:
        with self._lock:
            result = self._conn.execute("PRAGMA integrity_check").fetchone()[0]
            require(result == "ok", "LEDGER_INTEGRITY_FAILED")
            require(not self._conn.execute("PRAGMA foreign_key_check").fetchall(),
                    "LEDGER_FOREIGN_KEY_FAILED")
            return result

    def counts(self, tenant_id: str | None = None) -> dict[str, int]:
        tables = ("events", "runs", "transitions", "approvals", "nonces", "outbox", "dlq")
        result = {}
        with self._lock:
            for table in tables:
                if tenant_id is None:
                    query, args = f"SELECT COUNT(*) FROM {table}", ()
                else:
                    query, args = (
                        f"SELECT COUNT(*) FROM {table} WHERE tenant_id=?", (tenant_id,)
                    )
                result[table] = self._conn.execute(query, args).fetchone()[0]
        return result
