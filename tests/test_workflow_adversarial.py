"""Adversarial regression tests for the CD-02 authorization, ledger and recovery corrections."""
from __future__ import annotations

import copy
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import multiprocessing
import os
import sqlite3
import tempfile
import threading
import unittest
from unittest import mock
from pathlib import Path

from security.approval import HmacSha256TestVerifier, canonical_approval_bytes
from security.contracts import ApprovalEnvelope, Grant, Principal, SecurityError
from security.core import EXPECTED_POLICY, policy_fingerprint
from workflow.commands import CommandScope, WorkflowCommands, _payload_digest
from workflow.compiler import compile_catalog, dry_run, validate_dag
from workflow.contracts import (
    MAX_ATTEMPTS, RunContract, RunOptions, WorkflowEvent, load_workflows,
    retry_decision, validate_c12_workflow, validate_workflow_catalog,
)
from workflow.ledger import Ledger
from workflow.migrations import MIGRATION_1, MIGRATION_2, SCHEMA_VERSION
from workflow.schema_validation import validate_document

NOW = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)
PAYLOAD = "a" * 64
POLICY = policy_fingerprint(EXPECTED_POLICY)
SOURCE_LOCK = "a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e"
APPROVAL_KEY = b"synthetic-workflow-approval-key-never-production"


def make_event(**changes):
    values = dict(
        event_id="event-1", event_type="work_order.ready",
        occurred_at=NOW - timedelta(seconds=1), received_at=NOW,
        producer="executor", subject_ref="work-order-1", tenant_id="tenant-1",
        correlation_id="corr-1", idempotency_key="idem-1", payload_ref="payload-ref-1",
        payload_sha256=PAYLOAD, data_classification="INTERNAL", risk="STANDARD",
    )
    values.update(changes)
    return WorkflowEvent(**values)


class TestLedger(Ledger):
    """Storage fixture; command-boundary tests use WorkflowCommands."""

    def create_run(self, run_id="run-1", event=None, deadline=None):
        event = event or make_event()
        deadline = deadline or NOW + timedelta(hours=1)
        self._create_run(run_id, "tenant-1", "project-1", "task-1", "NLE-WF-GOV-03",
                         "0.1.0", event, NOW, deadline, SOURCE_LOCK)
        return event

    def run(self, run_id, tenant_id="tenant-1"):
        return super().run(run_id, tenant_id)

    def transition(self, run_id, target, event_id=None, expected_revision=None,
                   lease_owner=None, lease_epoch=None, reconciliation_ref=None):
        current = self.run(run_id)
        revision = current["revision"] if expected_revision is None else expected_revision
        return self._transition(run_id, "tenant-1", target, event_id, NOW, revision,
                                lease_owner, lease_epoch, reconciliation_ref)

    def claim_lease(self, run_id, owner, now, ttl_seconds=30):
        revision = self.run(run_id)["revision"]
        return self._claim_lease(
            run_id, "tenant-1", owner, now, ttl_seconds, revision,
        )

    def enqueue_outbox(self, run_id, event_id, payload_ref, now):
        revision = self.run(run_id)["revision"]
        return self._enqueue_outbox(
            run_id, "tenant-1", event_id, payload_ref, now, revision,
        )

    def dead_letter(self, run_id, reason, sanitized_ref, now):
        revision = self.run(run_id)["revision"]
        return self._dead_letter(
            run_id, "tenant-1", reason, sanitized_ref, now, revision,
        )

    def advance(self, run_id, *targets):
        for target in targets:
            current = self.run(run_id)
            lease = {}
            if current["state"] == "RUNNING":
                owner = "owner-a"
                epoch = self._claim_lease(
                    run_id, "tenant-1", owner, NOW, 30, current["revision"],
                )
                lease = {"lease_owner": owner, "lease_epoch": epoch}
            self.transition(run_id, target, None,
                            expected_revision=current["revision"], **lease)

    def recover(self, now=NOW):
        return self._recover(
            "tenant-1", "project-1", "task-1", "NLE-WF-GOV-03", now,
        )


def make_v2_ledger(path, *, partial_v3=False, event_risk="STANDARD",
                   risk_column_without_version=False):
    """Build a synthetic schema-2 ledger with duplicate legacy approval ids."""
    conn = sqlite3.connect(path)
    try:
        conn.executescript(MIGRATION_1)
        conn.executescript(MIGRATION_2)
        conn.executemany(
            "INSERT INTO schema_migrations(version, applied_at) VALUES(?,?)",
            [(1, NOW.isoformat()), (2, NOW.isoformat())],
        )
        for index in (1, 2):
            event_id = f"legacy-event-{index}"
            run_id = f"legacy-run-{index}"
            conn.execute(
                "INSERT INTO events(event_id,tenant_id,run_id,event_sha256,"
                "idempotency_key,event_type,correlation_id,payload_ref,payload_sha256,"
                "received_at,body_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (event_id, "tenant-1", run_id,
                 hashlib.sha256(event_id.encode()).hexdigest(), f"idem-{index}",
                 "work_order.ready", f"corr-{index}", f"payload-{index}", PAYLOAD,
                 NOW.isoformat(), json.dumps({"risk": event_risk})),
            )
            conn.execute(
                "INSERT INTO runs(run_id,tenant_id,project_id,task_id,workflow_id,"
                "workflow_version,event_id,correlation_id,state,revision,attempts,"
                "source_lock_sha256,deadline_at,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (run_id, "tenant-1", "project-1", "task-1", "NLE-WF-GOV-03",
                 "0.1.0", event_id, f"corr-{index}", "RECEIVED", 0, 0,
                 SOURCE_LOCK, (NOW + timedelta(hours=1)).isoformat(),
                 NOW.isoformat(), NOW.isoformat()),
            )
            conn.execute(
                "INSERT INTO approvals(approval_id,run_id,tenant_id,approver_id,action,"
                "payload_sha256,policy_sha256,nonce,expires_at,result,created_at) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                ("legacy-duplicate", run_id, "tenant-1", "legacy-approver",
                 "workflow.run.create", PAYLOAD, POLICY, f"legacy-nonce-{index}",
                 (NOW + timedelta(hours=1)).isoformat(), "AUTHORIZED_INTERNAL_ONLY",
                 NOW.isoformat()),
            )
        if partial_v3:
            conn.execute("CREATE TABLE approvals_v3 (partial TEXT)")
        if risk_column_without_version:
            conn.execute("ALTER TABLE runs ADD COLUMN risk TEXT NOT NULL DEFAULT 'STANDARD'")
            conn.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES(3,?)",
                (NOW.isoformat(),),
            )
        conn.commit()
    finally:
        conn.close()


def _open_worker(path, queue):
    try:
        return TestLedger(path)
    except BaseException as exc:
        queue.put(f"ERROR:OPEN:{type(exc).__name__}")
        return None


def _process_consume(path, nonce, now_iso, expiry_iso, queue):
    ledger = _open_worker(path, queue)
    if ledger is None:
        return
    try:
        now = datetime.fromisoformat(now_iso)
        expiry = datetime.fromisoformat(expiry_iso)
        _, outcome = ledger._consume_outcome(nonce, expiry, now)
        queue.put(outcome.value)
    except BaseException as exc:
        queue.put(f"ERROR:{type(exc).__name__}")
    finally:
        ledger.close()


def _process_create_same(path, queue):
    ledger = _open_worker(path, queue)
    if ledger is None:
        return
    try:
        ledger.create_run("run-shared")
        queue.put("CREATED")
    except SecurityError:
        queue.put("DUPLICATE")
    except sqlite3.Error:
        queue.put("STORAGE_ERROR")
    except BaseException as exc:
        queue.put(f"ERROR:{type(exc).__name__}")
    finally:
        ledger.close()


def _process_create_distinct(path, index, queue):
    ledger = _open_worker(path, queue)
    if ledger is None:
        return
    try:
        event = make_event(
            event_id=f"event-distinct-{index}",
            idempotency_key=f"idem-distinct-{index}",
        )
        ledger.create_run(f"run-distinct-{index}", event=event)
        queue.put("CREATED")
    except SecurityError:
        queue.put("REJECTED")
    except sqlite3.Error:
        queue.put("STORAGE_ERROR")
    except BaseException as exc:
        queue.put(f"ERROR:{type(exc).__name__}")
    finally:
        ledger.close()


def _process_claim(path, owner, queue):
    ledger = _open_worker(path, queue)
    if ledger is None:
        return
    try:
        ledger.claim_lease("run-1", owner, NOW, 30)
        queue.put("CLAIMED")
    except SecurityError:
        queue.put("DENIED")
    except sqlite3.Error:
        queue.put("STORAGE_ERROR")
    except BaseException as exc:
        queue.put(f"ERROR:{type(exc).__name__}")
    finally:
        ledger.close()


def _process_recover(path, queue):
    ledger = _open_worker(path, queue)
    if ledger is None:
        return
    try:
        result = ledger.recover(NOW)
        queue.put(f"RETRY:{result['retry_wait']}")
    except SecurityError:
        queue.put("DENIED")
    except sqlite3.Error:
        queue.put("STORAGE_ERROR")
    except BaseException as exc:
        queue.put(f"ERROR:{type(exc).__name__}")
    finally:
        ledger.close()


def _process_crash(path, now_iso, expiry_iso):
    ledger = TestLedger(path)
    now = datetime.fromisoformat(now_iso)
    expiry = datetime.fromisoformat(expiry_iso)
    with ledger._transaction():
        ledger._consume("crash-nonce", expiry, now)
        os._exit(7)


def grant(action, target="run-1", tenant="tenant-1", risk="ELEVATED"):
    return Grant(
        grant_id=f"grant-{action}", principal_id="agent-1", action=action,
        target_id=target, tenant_id=tenant, project_id="project-1", task_id="task-1",
        workflow_id="NLE-WF-QNT-01", skill_id="workflow-skill", host_id="host-1",
        provider_id="provider-local", risk=risk, policy_sha256=POLICY, policy_epoch=1,
        issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(minutes=5),
        revoked=False, max_spend_usd=Decimal("0"), external_effects="DENY",
    )


COMMAND_SCOPE = CommandScope(
    actor=Principal("agent-1", "agent", "tenant-1", "project-1", "host-1", "ACTIVE", 1),
    tenant_id="tenant-1", project_id="project-1", task_id="task-1",
    workflow_id="NLE-WF-QNT-01",
)


def commands(ledger, grants):
    return WorkflowCommands(
        ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
        risk="ELEVATED", grants=tuple(grants),
    )


def create_payload(event, *, deadline=None, policy_epoch=1, agent_id=None,
                   skill_lock_id=None, skill_lock_version=None, skill_lock_hash=None,
                   model_id=None, quota=0, output_ref=None, evidence_ref=None):
    deadline = deadline or NOW + timedelta(hours=1)
    return _payload_digest(
        "workflow.run.create", event_sha256=event.digest(),
        workflow_version="0.1.0", deadline_at=deadline.isoformat(),
        gate="INTERNAL_ONLY", activation="DISABLED",
        agent_id=agent_id or event.producer, skill_lock_id=skill_lock_id,
        skill_lock_version=skill_lock_version, skill_lock_hash=skill_lock_hash,
        model_id=model_id, quota=quota, output_ref=output_ref,
        evidence_ref=evidence_ref, policy_epoch=policy_epoch,
    )


def append_payload(event, run_id, *, policy_epoch=1):
    return _payload_digest(
        "workflow.event.append", event_sha256=event.digest(), run_id=run_id,
        policy_epoch=policy_epoch,
    )


def make_approval(payload_sha256, *, nonce="0123456789abcdefghijklmnopqrstuv",
                  approval_id="approval-1", action="workflow.run.create",
                  target_id="run-1"):
    approval = ApprovalEnvelope(
        approval_id=approval_id, actor_id="agent-1", approver_id="human-owner",
        approver_kind="human", approver_role="OWNER", action=action,
        target_id=target_id, tenant_id="tenant-1", project_id="project-1",
        task_id="task-1", workflow_id="NLE-WF-QNT-01", skill_id="workflow-skill",
        host_id="host-1", provider_id="provider-local", risk="HIGH_ASSURANCE",
        payload_sha256=payload_sha256, policy_sha256=POLICY,
        evidence_refs=("evidence-001",), max_spend_usd=Decimal("0"), nonce=nonce,
        issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(minutes=5),
    )
    signature = hmac.new(
        APPROVAL_KEY, canonical_approval_bytes(approval), hashlib.sha256
    ).hexdigest()
    return approval, signature


class CommandBoundaryTests(unittest.TestCase):
    def test_mutation_without_grant_is_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                command = commands(ledger, [])
                event = make_event()
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    command.create_run("run-1", "0.1.0", event, NOW, deadline)
                self.assertEqual(ledger.counts()["runs"], 0)

    def test_wrong_tenant_grant_is_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                command = commands(
                    ledger, [grant("workflow.run.create", tenant="tenant-2")]
                )
                event = make_event()
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    command.create_run("run-1", "0.1.0", event, NOW, deadline)
                self.assertEqual(ledger.counts()["runs"], 0)

    def test_authorized_create_and_transition(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                commands(
                    ledger, [grant("workflow.run.create")]
                ).create_run("run-1", "0.1.0", event, NOW, NOW + timedelta(hours=1))
                commands(
                    ledger, [grant("workflow.run.transition.RECEIVED.VALIDATED")]
                ).transition("run-1", "VALIDATED", event.event_id, NOW,
                             expected_revision=0, payload_sha256=PAYLOAD)
                self.assertEqual(ledger.run("run-1")["state"], "VALIDATED")

    def test_cross_project_task_workflow_scope_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                variants = (
                    ("project-2", "task-1", "NLE-WF-GOV-03"),
                    ("project-1", "task-2", "NLE-WF-GOV-03"),
                    ("project-1", "task-1", "NLE-WF-QNT-01"),
                )
                for index, (project, task, workflow) in enumerate(variants, 1):
                    event = make_event(
                        event_id=f"event-scope-{index}",
                        idempotency_key=f"idem-scope-{index}",
                    )
                    ledger._create_run(
                        f"run-scope-{index}", "tenant-1", project, task, workflow,
                        "0.1.0", event, NOW, NOW + timedelta(hours=1), SOURCE_LOCK,
                        RunOptions(risk="ELEVATED"),
                    )
                    command = commands(ledger, [])
                    with self.assertRaises(SecurityError):
                        command.transition(
                            f"run-scope-{index}", "VALIDATED", event.event_id, NOW,
                            expected_revision=0, payload_sha256=PAYLOAD,
                        )
                    self.assertEqual(
                        ledger.run(f"run-scope-{index}")["state"], "RECEIVED",
                    )

    def test_recovery_is_limited_to_authorized_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event(event_id="event-other", idempotency_key="idem-other")
                ledger._create_run(
                    "run-other", "tenant-1", "project-2", "task-1",
                    "NLE-WF-GOV-03", "0.1.0", event, NOW,
                    NOW + timedelta(hours=1), SOURCE_LOCK,
                    RunOptions(risk="ELEVATED"),
                )
                ledger.transition("run-other", "VALIDATED")
                ledger.transition("run-other", "QUEUED")
                ledger.transition("run-other", "RUNNING")
                command = commands(
                    ledger, [grant("workflow.recovery.run", target="tenant-1")]
                )
                command.recover(NOW)
                self.assertEqual(ledger.run("run-other")["state"], "RUNNING")

    def test_event_risk_cannot_be_downgraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                command = commands(ledger, [grant("workflow.run.create")])
                event = make_event(risk="HIGH_ASSURANCE")
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    command.create_run("run-1", "0.1.0", event, NOW, deadline)

    def test_stale_revision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                commands(ledger, [grant("workflow.run.create")]).create_run(
                    "run-1", "0.1.0", event, NOW, NOW + timedelta(hours=1)
                )
                transition = commands(
                    ledger, [grant("workflow.run.transition.RECEIVED.VALIDATED")]
                )
                with self.assertRaises(SecurityError):
                    transition.transition(
                        "run-1", "VALIDATED", event.event_id, NOW,
                        expected_revision=99, payload_sha256=PAYLOAD
                    )


class HighAssuranceCommandTests(unittest.TestCase):
    def test_command_persists_approval_and_nonce(self):
        event = make_event()
        approval, signature = make_approval(create_payload(event))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            with TestLedger(path) as ledger:
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.run.create", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                command.create_run("run-1", "0.1.0", event, NOW, NOW + timedelta(hours=1))
                counts = ledger.counts()
                self.assertEqual(counts["approvals"], 1)
                self.assertEqual(counts["nonces"], 1)
                run = ledger.run("run-1")
                self.assertEqual(run["approval_id"], "approval-1")
                self.assertEqual(run["approval_ref"], "approval-1")
                self.assertEqual(run["idempotency_key"], event.idempotency_key)
                self.assertEqual(run["agent_id"], event.producer)
                self.assertEqual(run["data_classification"], event.data_classification)
                self.assertEqual(run["inputs_ref"], event.payload_ref)
                self.assertEqual(run["quota"], 0)
                self.assertEqual(run["status"], "RECEIVED")
                self.assertEqual(run["gate"], "INTERNAL_ONLY")
                self.assertEqual(run["activation"], "DISABLED")
                row = ledger._conn.execute(
                    "SELECT run_id,target_id,actor_id,project_id,task_id,workflow_id,"
                    "risk,policy_epoch,action,approver_role,evidence_refs_json,"
                    "max_spend_usd,issued_at FROM approvals WHERE approval_id=?",
                    ("approval-1",),
                ).fetchone()
                self.assertEqual(
                    {key: row[key] for key in (
                        "run_id", "target_id", "actor_id", "project_id", "task_id",
                        "workflow_id", "risk", "policy_epoch", "action",
                        "approver_role", "max_spend_usd",
                    )},
                    {"run_id": "run-1", "target_id": "run-1", "actor_id": "agent-1",
                     "project_id": "project-1", "task_id": "task-1",
                     "workflow_id": "NLE-WF-QNT-01", "risk": "HIGH_ASSURANCE",
                     "policy_epoch": 1, "action": "workflow.run.create",
                     "approver_role": "OWNER", "max_spend_usd": "0"},
                )
                self.assertEqual(json.loads(row["evidence_refs_json"]),
                                 ["evidence-001"])
                self.assertEqual(row["issued_at"], (NOW - timedelta(minutes=1)).isoformat())
            with TestLedger(path) as ledger:
                replay = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.run.create", target="run-2", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                event = make_event(event_id="event-2", idempotency_key="idem-2")
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    replay.create_run("run-2", "0.1.0", event, NOW, deadline)

    def test_failed_mutation_rolls_back_approval_and_nonce(self):
        event = make_event()
        approval, signature = make_approval(
            create_payload(event), nonce="rollbacknonce0123456789abcdef",
            approval_id="approval-rollback",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run("run-1", event=event)
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.run.create", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    command.create_run("run-1", "0.1.0", event, NOW, deadline)
                counts = ledger.counts()
                self.assertEqual(counts["nonces"], 0)
                self.assertEqual(counts["approvals"], 0)

    def test_approved_append_event_persists_run_scope(self):
        run_event = make_event()
        appended = make_event(event_id="event-2", idempotency_key="idem-2")
        approval, signature = make_approval(
            append_payload(appended, "run-1"), nonce="appendnonce0123456789abcdef",
            approval_id="approval-append", action="workflow.event.append",
            target_id=appended.event_id,
        )
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                commands(ledger, [grant("workflow.run.create")]).create_run(
                    "run-1", "0.1.0", run_event, NOW, NOW + timedelta(hours=1)
                )
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.event.append", target=appended.event_id,
                                  risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                command.append_event(appended, "run-1", NOW)
                self.assertEqual(ledger.counts()["approvals"], 1)
                row = ledger._conn.execute(
                    "SELECT run_id,target_id,action FROM approvals WHERE approval_id=?",
                    ("approval-append",),
                ).fetchone()
                self.assertEqual(
                    dict(row),
                    {"run_id": "run-1", "target_id": "event-2",
                     "action": "workflow.event.append"},
                )

    def test_approval_payload_binds_run_options(self):
        event = make_event()
        approval, signature = make_approval(create_payload(event))
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.run.create", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    command.create_run(
                        "run-1", "0.1.0", event, NOW, deadline,
                        options=RunOptions(
                            agent_id="agent-B", skill_lock_id="skill-B",
                            skill_lock_version="9.9.9", skill_lock_hash="b" * 64,
                            model_id="model-B", quota=1, output_ref="out-B",
                            evidence_ref="ev-B",
                        ),
                    )
                self.assertEqual(ledger.counts()["runs"], 0)
                self.assertEqual(ledger.counts()["nonces"], 0)

    def test_run_agent_cannot_take_segregated_role(self):
        for agent in ("NLE-POSEIDON-CIO", "NLE-POSEIDON-RISK",
                      "NLE-ATHENA-PMO"):
            with self.subTest(agent=agent):
                with tempfile.TemporaryDirectory() as tmp:
                    with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                        command = commands(
                            ledger, [grant("workflow.run.create")]
                        )
                        event = make_event()
                        deadline = NOW + timedelta(hours=1)
                        with self.assertRaises(SecurityError):
                            command.create_run(
                                "run-1", "0.1.0", event, NOW, deadline,
                                options=RunOptions(agent_id=agent),
                            )
                        self.assertEqual(ledger.counts()["runs"], 0)

    def test_approval_payload_binds_append_run_id(self):
        run_event = make_event()
        appended = make_event(event_id="event-2", idempotency_key="idem-2")
        approval, signature = make_approval(
            append_payload(appended, "run-1"),
            nonce="appendrun0123456789abcdef", approval_id="approval-append-run",
            action="workflow.event.append", target_id=appended.event_id,
        )
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                commands(ledger, [grant("workflow.run.create")]).create_run(
                    "run-1", "0.1.0", run_event, NOW, NOW + timedelta(hours=1)
                )
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.event.append", target=appended.event_id,
                                  risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                with self.assertRaises(SecurityError):
                    command.append_event(appended, "run-2", NOW)
                self.assertEqual(ledger.counts()["events"], 1)

    def test_approval_payload_binds_outbox_parameters(self):
        run_event = make_event()
        approved_event = make_event(event_id="event-2", idempotency_key="idem-2")
        payload = _payload_digest(
            "workflow.outbox.enqueue", event_id=approved_event.event_id,
            payload_ref=approved_event.payload_ref, expected_revision=0,
            lease_owner=None, lease_epoch=None, policy_epoch=1,
        )
        approval, signature = make_approval(
            payload, nonce="outboxnonce0123456789abcdef",
            approval_id="approval-outbox",
            action="workflow.outbox.enqueue.RECEIVED", target_id="run-1",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                commands(ledger, [grant("workflow.run.create")]).create_run(
                    "run-1", "0.1.0", run_event, NOW, NOW + timedelta(hours=1)
                )
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.outbox.enqueue.RECEIVED",
                                  risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                with self.assertRaises(SecurityError):
                    command.enqueue_outbox("run-1", "event-3", "payload-3", NOW,
                                           expected_revision=0)
                self.assertEqual(ledger.counts()["outbox"], 0)

    def test_human_gate_requires_high_assurance_boundary(self):
        scope = CommandScope(
            actor=COMMAND_SCOPE.actor, tenant_id="tenant-1", project_id="project-1",
            task_id="task-1", workflow_id="NLE-WF-GOV-01",
        )
        with self.assertRaises(SecurityError):
            WorkflowCommands(
                None, scope, policy_sha256=POLICY, policy_epoch=1,
                risk="ELEVATED",
            )

    def test_unknown_workflow_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                command = commands(ledger, [grant("workflow.run.create")])
                event = make_event()
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    command.create_run("run-1", "9.9.9", event, NOW, deadline)
                self.assertEqual(ledger.counts()["runs"], 0)

    def test_unverified_approval_is_not_persisted(self):
        event = make_event()
        approval, signature = make_approval(create_payload(event))
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="ELEVATED", grants=(grant("workflow.run.create"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    command.create_run("run-1", "0.1.0", event, NOW, deadline)
                self.assertEqual(ledger.counts()["runs"], 0)
                self.assertEqual(ledger.counts()["nonces"], 0)

    def test_transition_requires_state_specific_grant(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                commands(ledger, [grant("workflow.run.create")]).create_run(
                    "run-1", "0.1.0", event, NOW, NOW + timedelta(hours=1)
                )
                command = commands(ledger, [grant("workflow.run.transition")])
                with self.assertRaises(SecurityError):
                    command.transition(
                        "run-1", "VALIDATED", event.event_id, NOW,
                        expected_revision=0, payload_sha256=PAYLOAD,
                    )
                self.assertEqual(ledger.run("run-1")["state"], "RECEIVED")

    def test_high_assurance_run_rejects_standard_transition(self):
        event = make_event(risk="HIGH_ASSURANCE")
        approval, signature = make_approval(
            create_payload(event), nonce="riskfloornonce0123456789abcdef",
            approval_id="approval-risk-floor",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                high = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.run.create", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                high.create_run("run-1", "0.1.0", event, NOW, NOW + timedelta(hours=1))
                standard = commands(
                    ledger, [grant("workflow.run.transition.RECEIVED.VALIDATED")]
                )
                with self.assertRaises(SecurityError):
                    standard.transition("run-1", "VALIDATED", event.event_id, NOW,
                                        expected_revision=0, payload_sha256=PAYLOAD)

    def test_approval_policy_epoch_is_bound(self):
        event = make_event()
        approval, signature = make_approval(
            create_payload(event, policy_epoch=2),
            nonce="epochnonce0123456789abcdef", approval_id="approval-epoch",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.run.create", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    command.create_run("run-1", "0.1.0", event, NOW, deadline)
                self.assertEqual(ledger.counts()["runs"], 0)


class LedgerIntegrityTests(unittest.TestCase):
    def test_cross_tenant_references_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = ledger.create_run()
                with self.assertRaises(SecurityError):
                    ledger._transition("run-1", "tenant-2", "VALIDATED", event.event_id, NOW, 0)
                with self.assertRaises(SecurityError):
                    ledger._enqueue_outbox("run-1", "tenant-2", event.event_id,
                                           event.payload_ref, NOW, 0)

    def test_append_event_binds_full_persisted_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                variants = (
                    ("project-2", "task-1", "NLE-WF-QNT-01"),
                    ("project-1", "task-2", "NLE-WF-QNT-01"),
                    ("project-1", "task-1", "NLE-WF-QNT-02"),
                )
                for index, (project, task, workflow) in enumerate(variants, 1):
                    run_event = make_event(
                        event_id=f"event-base-{index}",
                        idempotency_key=f"idem-base-{index}",
                    )
                    ledger._create_run(
                        f"run-{index}", "tenant-1", project, task, workflow,
                        "0.1.0", run_event, NOW, NOW + timedelta(hours=1), SOURCE_LOCK,
                        RunOptions(risk="ELEVATED"),
                    )
                    appended = make_event(
                        event_id=f"event-append-{index}",
                        idempotency_key=f"idem-append-{index}",
                    )
                    command = commands(
                        ledger,
                        [grant("workflow.event.append", target=appended.event_id)],
                    )
                    with self.assertRaises(SecurityError):
                        command.append_event(appended, f"run-{index}", NOW)
                self.assertEqual(ledger.counts()["events"], 3)

    def test_append_event_requires_existing_same_tenant_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                ghost = make_event(event_id="event-ghost", idempotency_key="idem-ghost")
                with self.assertRaises(SecurityError):
                    ledger._append_event(ghost, "ghost-run")
                cross = make_event(event_id="event-cross", idempotency_key="idem-cross",
                                   tenant_id="tenant-2")
                with self.assertRaises(SecurityError):
                    ledger._append_event(cross, "run-1")
                self.assertEqual(ledger.counts()["events"], 1)

    def test_blocked_state_has_exit_and_no_outbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "BLOCKED")
                revision = ledger.run("run-1")["revision"]
                with self.assertRaises(SecurityError):
                    ledger._enqueue_outbox("run-1", "tenant-1", event.event_id,
                                           event.payload_ref, NOW, revision)
                ledger.transition("run-1", "CANCELLED")
                self.assertEqual(ledger.run("run-1")["state"], "CANCELLED")

    def test_migration_resume_preserves_full_approval_scope(self):
        event = make_event()
        approval, signature = make_approval(
            create_payload(event), nonce="resumenonce0123456789abcdef",
            approval_id="approval-resume",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            with TestLedger(path) as ledger:
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.run.create", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                command.create_run("run-1", "0.1.0", event, NOW, NOW + timedelta(hours=1))
                ledger._conn.execute("DELETE FROM schema_migrations WHERE version>=3")
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.schema_version, SCHEMA_VERSION)
                row = ledger._conn.execute(
                    "SELECT actor_id,approver_role,evidence_refs_json,policy_epoch "
                    "FROM approvals WHERE approval_id=?",
                    ("approval-resume",),
                ).fetchone()
                self.assertEqual(row["actor_id"], "agent-1")
                self.assertEqual(row["approver_role"], "OWNER")
                self.assertEqual(json.loads(row["evidence_refs_json"]), ["evidence-001"])
                self.assertEqual(row["policy_epoch"], 1)

    def test_migration_fails_closed_without_approvals_or_complete_v3(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.sqlite3"
            make_v2_ledger(path)
            conn = sqlite3.connect(path)
            conn.execute("DROP TABLE approvals")
            conn.execute("CREATE TABLE approvals_v3 (partial TEXT)")
            conn.commit()
            conn.close()
            with self.assertRaises(Exception):
                Ledger(path)
            conn = sqlite3.connect(path)
            version = conn.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()[0]
            conn.close()
            self.assertEqual(version, 2)

    def test_migration_v3_rejects_partial_with_only_five_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "partial-five.sqlite3"
            make_v2_ledger(path)
            conn = sqlite3.connect(path)
            conn.execute("DROP TABLE approvals")
            conn.execute(
                "CREATE TABLE approvals_v3 (approval_id TEXT, tenant_id TEXT, "
                "approver_role TEXT, evidence_refs_json TEXT, run_id TEXT)"
            )
            conn.commit()
            conn.close()
            with self.assertRaises(Exception):
                Ledger(path)
            conn = sqlite3.connect(path)
            version = conn.execute(
                "SELECT MAX(version) FROM schema_migrations"
            ).fetchone()[0]
            conn.close()
            self.assertEqual(version, 2)

    def test_dlq_quarantines_atomically_and_blocks_outbox(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = ledger.create_run()
                ledger.advance("run-1", "VALIDATED")
                ledger.dead_letter(
                    "run-1", "INTEGRITY_FAILURE", "ref-sanitized", NOW,
                )
                current = ledger.run("run-1")
                self.assertEqual(current["state"], "QUARANTINED")
                self.assertEqual(current["status"], "QUARANTINED")
                self.assertEqual(ledger.counts()["dlq"], 1)
                with self.assertRaises(SecurityError):
                    ledger._enqueue_outbox(
                        "run-1", "tenant-1", event.event_id, event.payload_ref,
                        NOW, current["revision"],
                    )
                with self.assertRaises(SecurityError):
                    ledger.transition("run-1", "QUEUED")
                audit = ledger._conn.execute(
                    "SELECT actor_id,action FROM audit_events WHERE run_id=? "
                    "ORDER BY audit_id DESC LIMIT 1",
                    ("run-1",),
                ).fetchone()
                self.assertEqual(dict(audit),
                                 {"actor_id": "system",
                                  "action": "workflow.dlq.record"})

    def test_outbox_audit_rolls_back_with_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = ledger.create_run()
                ledger.enqueue_outbox(
                    "run-1", event.event_id, event.payload_ref, NOW,
                )
                self.assertEqual(ledger.counts()["outbox"], 1)
                audit_count = ledger._conn.execute(
                    "SELECT COUNT(*) FROM audit_events WHERE run_id=?",
                    ("run-1",),
                ).fetchone()[0]
                self.assertEqual(audit_count, 1)
                with self.assertRaises(SecurityError):
                    ledger.enqueue_outbox(
                        "run-1", event.event_id, event.payload_ref, NOW,
                    )
                self.assertEqual(ledger.counts()["outbox"], 1)
                self.assertEqual(
                    ledger._conn.execute(
                        "SELECT COUNT(*) FROM audit_events WHERE run_id=?",
                        ("run-1",),
                    ).fetchone()[0],
                    audit_count,
                )

    def test_migration_v5_audit_actor_upgrade_is_resumable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            with TestLedger(path):
                pass
            conn = sqlite3.connect(path)
            conn.execute("ALTER TABLE audit_events DROP COLUMN actor_id")
            conn.execute("DELETE FROM schema_migrations WHERE version=6")
            conn.commit()
            conn.close()
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.schema_version, SCHEMA_VERSION)
                columns = {
                    row[1] for row in ledger._conn.execute(
                        "PRAGMA table_info(audit_events)"
                    )
                }
                self.assertIn("actor_id", columns)
                ledger.create_run()
                revision = ledger.run("run-1")["revision"]
                ledger._set_flags("run-1", "tenant-1", NOW, stale=True,
                                  expected_revision=revision, actor_id="agent-1")
                actor = ledger._conn.execute(
                    "SELECT actor_id FROM audit_events WHERE run_id=?",
                    ("run-1",),
                ).fetchone()[0]
                self.assertEqual(actor, "agent-1")

    def test_migration_backfills_legacy_high_risk_and_resumes_v4(self):
        with tempfile.TemporaryDirectory() as tmp:
            high = Path(tmp) / "high.sqlite3"
            make_v2_ledger(high, event_risk="HIGH_ASSURANCE")
            with TestLedger(high) as ledger:
                self.assertEqual(ledger.schema_version, SCHEMA_VERSION)
                self.assertEqual(ledger.run("legacy-run-1")["risk"], "HIGH_ASSURANCE")
            resumable = Path(tmp) / "resumable.sqlite3"
            make_v2_ledger(resumable, event_risk="HIGH_ASSURANCE",
                           risk_column_without_version=True)
            with TestLedger(resumable) as ledger:
                self.assertEqual(ledger.schema_version, SCHEMA_VERSION)
                self.assertEqual(ledger.run("legacy-run-1")["risk"], "HIGH_ASSURANCE")
            nonhashable = Path(tmp) / "nonhashable.sqlite3"
            make_v2_ledger(nonhashable, event_risk=["HIGH_ASSURANCE"])
            with TestLedger(nonhashable) as ledger:
                self.assertEqual(ledger.run("legacy-run-1")["risk"], "HIGH_ASSURANCE")
            bogus = Path(tmp) / "bogus.sqlite3"
            make_v2_ledger(bogus, risk_column_without_version=True)
            conn = sqlite3.connect(bogus)
            conn.execute("UPDATE runs SET risk='BOGUS'")
            conn.commit()
            conn.close()
            with TestLedger(bogus) as ledger:
                self.assertEqual(ledger.run("legacy-run-1")["risk"], "HIGH_ASSURANCE")

    def test_migration_handles_legacy_duplicates_and_partial_v3(self):
        with tempfile.TemporaryDirectory() as tmp:
            duplicate = Path(tmp) / "duplicate.sqlite3"
            make_v2_ledger(duplicate)
            with TestLedger(duplicate) as ledger:
                self.assertEqual(ledger.schema_version, SCHEMA_VERSION)
                self.assertEqual(ledger.counts()["approvals"], 2)
                self.assertEqual(ledger.integrity(), "ok")
            partial = Path(tmp) / "partial.sqlite3"
            make_v2_ledger(partial, partial_v3=True)
            with TestLedger(partial) as ledger:
                self.assertEqual(ledger.schema_version, SCHEMA_VERSION)
                self.assertEqual(ledger.counts()["approvals"], 2)
                self.assertEqual(ledger.integrity(), "ok")

    def test_outbox_requires_revision_and_lease(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
                revision = ledger.run("run-1")["revision"]
                with self.assertRaises(SecurityError):
                    ledger._enqueue_outbox(
                        "run-1", "tenant-1", event.event_id, event.payload_ref,
                        NOW, revision - 1,
                    )
                with self.assertRaises(SecurityError):
                    ledger._enqueue_outbox(
                        "run-1", "tenant-1", event.event_id, event.payload_ref,
                        NOW, revision,
                    )
                epoch = ledger.claim_lease("run-1", "owner-a", NOW, 30)
                ledger._enqueue_outbox(
                    "run-1", "tenant-1", event.event_id, event.payload_ref,
                    NOW, revision, "owner-a", epoch,
                )
                self.assertEqual(ledger.counts()["outbox"], 1)

    def test_flags_increment_revision_and_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                revision = ledger.run("run-1")["revision"]
                ledger._set_flags(
                    "run-1", "tenant-1", NOW, stale=True, expected_revision=revision,
                )
                current = ledger.run("run-1")
                self.assertEqual(current["revision"], revision + 1)
                self.assertEqual(current["stale"], 1)
                audit = ledger._conn.execute(
                    "SELECT action,revision FROM audit_events WHERE run_id=?",
                    ("run-1",),
                ).fetchall()
                self.assertEqual([(row["action"], row["revision"]) for row in audit],
                                 [("SET_FLAGS", revision + 1)])

    def test_outbox_rejects_terminal_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING", "REVIEW",
                               "APPROVED", "VERIFIED", "COMPLETED")
                revision = ledger.run("run-1")["revision"]
                with self.assertRaises(SecurityError):
                    ledger._enqueue_outbox("run-1", "tenant-1", event.event_id,
                                           event.payload_ref, NOW, revision)

    def test_idempotency_with_divergent_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                event = make_event(event_id="event-2", payload_sha256="b" * 64)
                deadline = NOW + timedelta(hours=1)
                with self.assertRaises(SecurityError):
                    ledger._create_run("run-2", "tenant-1", "project-1", "task-1",
                                       "NLE-WF-GOV-03", "0.1.0", event,
                                       NOW, deadline, SOURCE_LOCK)
                self.assertEqual(ledger.counts()["events"], 1)

    def test_migration_version_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                self.assertEqual(ledger.schema_version, SCHEMA_VERSION)
                self.assertEqual(ledger.integrity(), "ok")
                self.assertEqual(
                    ledger._conn.execute("PRAGMA journal_mode").fetchone()[0], "wal"
                )

    def test_idempotency_key_divergence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                event = make_event(event_id="event-2", payload_sha256="b" * 64)
                with self.assertRaises(SecurityError):
                    ledger._append_event(event)


class NonceRecoveryTests(unittest.TestCase):
    def test_expired_and_concurrent_nonce(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            with TestLedger(path) as ledger:
                expired_at = NOW - timedelta(seconds=1)
                with self.assertRaises(SecurityError):
                    ledger._consume("expired", expired_at, NOW)
            results = []
            lock = threading.Lock()
            barrier = threading.Barrier(6)

            def worker():
                ledger = TestLedger(path)
                try:
                    barrier.wait(timeout=5)
                    _, outcome = ledger._consume_outcome(
                        "same", NOW + timedelta(minutes=1), NOW,
                    )
                    value = outcome.value
                except BaseException as exc:
                    value = f"ERROR:{type(exc).__name__}"
                finally:
                    ledger.close()
                with lock:
                    results.append(value)

            threads = [threading.Thread(target=worker) for _ in range(6)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(results.count("COMMITTED"), 1)
            self.assertEqual(results.count("REPLAY_REJECTED"), 5)
            self.assertFalse(any(item.startswith("ERROR") for item in results))

    def test_same_instance_threads_are_serialized(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            ledger = TestLedger(path)
            results = []
            lock = threading.Lock()
            barrier = threading.Barrier(6)

            def worker():
                try:
                    barrier.wait(timeout=5)
                    _, outcome = ledger._consume_outcome(
                        "shared", NOW + timedelta(minutes=1), NOW,
                    )
                    value = outcome.value
                except BaseException as exc:
                    value = f"ERROR:{type(exc).__name__}"
                with lock:
                    results.append(value)

            threads = [threading.Thread(target=worker) for _ in range(6)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            ledger.close()
            self.assertEqual(results.count("COMMITTED"), 1)
            self.assertEqual(results.count("REPLAY_REJECTED"), 5)
            self.assertFalse(any(item.startswith("ERROR") for item in results))

    def test_independent_processes_share_nonce(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "ledger.sqlite3")
            with TestLedger(path):
                pass
            context = multiprocessing.get_context("spawn")
            queue = context.Queue()
            now_iso = NOW.isoformat()
            expiry_iso = (NOW + timedelta(minutes=1)).isoformat()
            processes = [
                context.Process(
                    target=_process_consume,
                    args=(path, "process-nonce", now_iso, expiry_iso, queue),
                )
                for _ in range(4)
            ]
            for process in processes:
                process.start()
            for process in processes:
                process.join(timeout=60)
            outcomes = [queue.get(timeout=10) for _ in processes]
            self.assertEqual(outcomes.count("COMMITTED"), 1)
            self.assertEqual(outcomes.count("REPLAY_REJECTED"), 3)
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.counts()["nonces"], 1)
                self.assertEqual(ledger.integrity(), "ok")

    def test_crash_inside_transaction_rolls_back_nonce(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "ledger.sqlite3")
            with TestLedger(path):
                pass
            context = multiprocessing.get_context("spawn")
            process = context.Process(
                target=_process_crash,
                args=(path, NOW.isoformat(),
                      (NOW + timedelta(minutes=1)).isoformat()),
            )
            process.start()
            process.join(timeout=60)
            self.assertNotEqual(process.exitcode, 0)
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.counts()["nonces"], 0)
                self.assertEqual(ledger.integrity(), "ok")

    def test_approval_record_failure_rolls_back_command(self):
        event = make_event()
        approval, signature = make_approval(
            create_payload(event), nonce="rollbackapproval0123456789",
            approval_id="approval-failure",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.run.create", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                deadline = NOW + timedelta(hours=1)
                with mock.patch.object(
                    ledger, "_record_approval",
                    side_effect=RuntimeError("approval storage failed"),
                ):
                    with self.assertRaises(RuntimeError):
                        command.create_run("run-1", "0.1.0", event, NOW, deadline)
                counts = ledger.counts()
                self.assertEqual(counts["runs"], 0)
                self.assertEqual(counts["events"], 0)
                self.assertEqual(counts["nonces"], 0)

    def test_recovery_releases_lease_and_caps_retries(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING",
                               "RETRY_WAIT", "QUEUED", "RUNNING")
                revision = ledger.run("run-1")["revision"]
                ledger._claim_lease("run-1", "tenant-1", "owner-a",
                                    NOW - timedelta(minutes=2), 1, revision)
                result = ledger.recover()
                self.assertEqual(result["failed"], 1)
                self.assertEqual(ledger.run("run-1")["state"], "FAILED")
                self.assertIsNone(ledger.run("run-1")["lease_owner"])

    def test_recovery_fails_stale_or_expired_runs_without_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "stale.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
                revision = ledger.run("run-1")["revision"]
                ledger._set_flags("run-1", "tenant-1", NOW, stale=True, expected_revision=revision)
                result = ledger.recover()
                self.assertEqual(result["failed"], 1)
                self.assertEqual(ledger.run("run-1")["state"], "FAILED")
            with TestLedger(Path(tmp) / "deadline.sqlite3") as ledger:
                ledger.create_run(deadline=NOW + timedelta(seconds=30))
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
                result = ledger.recover(NOW + timedelta(minutes=1))
                self.assertEqual(result["failed"], 1)
                self.assertEqual(ledger.run("run-1")["state"], "FAILED")

    def test_claim_requires_revision_and_expired_lease_needs_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
                revision = ledger.run("run-1")["revision"]
                with self.assertRaises(SecurityError):
                    ledger._claim_lease(
                        "run-1", "tenant-1", "owner-a", NOW, 30, revision - 1,
                    )
                ledger._claim_lease(
                    "run-1", "tenant-1", "owner-a",
                    NOW - timedelta(minutes=2), 1, revision,
                )
                with self.assertRaises(SecurityError):
                    ledger._claim_lease(
                        "run-1", "tenant-1", "owner-b", NOW, 30, revision,
                    )
                result = ledger.recover()
                self.assertEqual(result["retry_wait"], 1)

    def test_effect_in_progress_can_be_claimed_and_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING", "REVIEW",
                               "APPROVED", "EFFECT_READY", "EFFECT_IN_PROGRESS")
                revision = ledger.run("run-1")["revision"]
                epoch = ledger._claim_lease("run-1", "tenant-1", "effect-owner", NOW, 30,
                                            revision)
                ledger._transition("run-1", "tenant-1", "VERIFIED", None, NOW,
                                   revision, "effect-owner", epoch)
                self.assertEqual(ledger.run("run-1")["state"], "VERIFIED")

    def test_recovery_never_exceeds_attempt_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
                ledger._conn.execute(
                    "UPDATE runs SET attempts=2 WHERE run_id=? AND tenant_id=?",
                    ("run-1", "tenant-1"),
                )
                result = ledger.recover()
                self.assertEqual(result["failed"], 1)
                row = ledger.run("run-1")
                self.assertEqual(row["state"], "FAILED")
                self.assertEqual(row["attempts"], MAX_ATTEMPTS)

    def test_revocation_and_retry_cap_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                revision = ledger.run("run-1")["revision"]
                ledger._set_flags("run-1", "tenant-1", NOW, revoked=True,
                                  expected_revision=revision)
                revision = ledger.run("run-1")["revision"]
                with self.assertRaises(SecurityError):
                    ledger._set_flags("run-1", "tenant-1", NOW, revoked=False,
                                      expected_revision=revision)
                event = make_event(event_id="event-2", idempotency_key="idem-2")
                ledger.create_run("run-2", event=event)
                ledger.advance("run-2", "VALIDATED", "QUEUED", "RUNNING",
                               "RETRY_WAIT", "QUEUED", "RUNNING")
                revision = ledger.run("run-2")["revision"]
                epoch = ledger._claim_lease("run-2", "tenant-1", "owner-a", NOW, 30,
                                            revision)
                with self.assertRaises(SecurityError):
                    ledger._transition("run-2", "tenant-1", "RETRY_WAIT", None, NOW,
                                       revision, "owner-a", epoch)

    def test_unknown_effect_requires_reconciliation_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING", "REVIEW",
                               "APPROVED", "EFFECT_READY", "EFFECT_IN_PROGRESS")
                ledger.recover()
                self.assertEqual(ledger.run("run-1")["state"], "UNKNOWN_EFFECT")
                with self.assertRaises(SecurityError):
                    ledger.transition("run-1", "VERIFIED")
                ledger.transition("run-1", "VERIFIED", reconciliation_ref="evidence-1")


class MultiprocessConcurrencyTests(unittest.TestCase):
    def test_same_run_and_idempotency_have_one_process_winner(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "ledger.sqlite3")
            with TestLedger(path):
                pass
            context = multiprocessing.get_context("spawn")
            queue = context.Queue()
            processes = [
                context.Process(target=_process_create_same, args=(path, queue))
                for _ in range(4)
            ]
            for process in processes:
                process.start()
            for process in processes:
                process.join(timeout=60)
            outcomes = [queue.get(timeout=10) for _ in processes]
            self.assertTrue(all(process.exitcode == 0 for process in processes))
            self.assertEqual(outcomes.count("CREATED"), 1, outcomes)
            self.assertEqual(outcomes.count("DUPLICATE"), 3, outcomes)
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.counts()["runs"], 1)
                self.assertEqual(ledger.counts()["events"], 1)
                self.assertEqual(ledger.integrity(), "ok")

    def test_distinct_events_from_processes_are_all_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "ledger.sqlite3")
            with TestLedger(path):
                pass
            context = multiprocessing.get_context("spawn")
            queue = context.Queue()
            processes = [
                context.Process(target=_process_create_distinct, args=(path, index, queue))
                for index in range(1, 5)
            ]
            for process in processes:
                process.start()
            for process in processes:
                process.join(timeout=60)
            outcomes = [queue.get(timeout=10) for _ in processes]
            self.assertTrue(all(process.exitcode == 0 for process in processes))
            self.assertEqual(outcomes.count("CREATED"), 4, outcomes)
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.counts()["runs"], 4)
                self.assertEqual(ledger.counts()["events"], 4)
                self.assertEqual(ledger.integrity(), "ok")

    def test_process_lease_fencing_has_single_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "ledger.sqlite3")
            with TestLedger(path) as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
            context = multiprocessing.get_context("spawn")
            queue = context.Queue()
            processes = [
                context.Process(
                    target=_process_claim, args=(path, f"owner-{index}", queue)
                )
                for index in range(1, 5)
            ]
            for process in processes:
                process.start()
            for process in processes:
                process.join(timeout=60)
            outcomes = [queue.get(timeout=10) for _ in processes]
            self.assertTrue(all(process.exitcode == 0 for process in processes))
            self.assertEqual(outcomes.count("CLAIMED"), 1)
            self.assertEqual(outcomes.count("DENIED"), 3)
            self.assertNotIn("STORAGE_ERROR", outcomes)
            with TestLedger(path) as ledger:
                self.assertIsNotNone(ledger.run("run-1")["lease_owner"])
                self.assertEqual(ledger.integrity(), "ok")

    def test_process_recovery_has_single_transition(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "ledger.sqlite3")
            with TestLedger(path) as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
            context = multiprocessing.get_context("spawn")
            queue = context.Queue()
            processes = [
                context.Process(target=_process_recover, args=(path, queue))
                for _ in range(4)
            ]
            for process in processes:
                process.start()
            for process in processes:
                process.join(timeout=60)
            outcomes = [queue.get(timeout=10) for _ in processes]
            self.assertTrue(all(process.exitcode == 0 for process in processes))
            self.assertNotIn("STORAGE_ERROR", outcomes)
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.run("run-1")["state"], "RETRY_WAIT")
                self.assertEqual(ledger.run("run-1")["attempts"], 1)
                transitions = ledger._conn.execute(
                    "SELECT COUNT(*) FROM transitions WHERE run_id=? "
                    "AND from_state='RUNNING' AND to_state='RETRY_WAIT'",
                    ("run-1",),
                ).fetchone()[0]
                self.assertEqual(transitions, 1)
                self.assertEqual(ledger.integrity(), "ok")


class CompilerAndC12Tests(unittest.TestCase):
    def test_compiler_and_dry_run_are_deterministic(self):
        first = compile_catalog()
        second = compile_catalog()
        self.assertEqual(first, second)
        self.assertEqual(first["summary"]["workflows"], 62)
        self.assertEqual(first["summary"]["grants"], 0)
        plan = dry_run("NLE-WF-GOV-03", "run-1", "tenant-1", NOW, NOW + timedelta(hours=1))
        self.assertFalse(plan["execution_allowed"])
        self.assertEqual(plan["schema"], "nexlabs.workflow-plan.v1")
        self.assertEqual(plan["workflow_version"], "0.1.0")
        for node in plan["dag"]["nodes"]:
            self.assertEqual(
                set(node),
                {"id", "step", "agent_id", "task", "scope", "autonomy_ceiling",
                 "eligible_packages", "external_effects"},
            )
        deadline = NOW + timedelta(hours=1)
        with self.assertRaises(SecurityError):
            dry_run("unknown", "run-1", "tenant-1", NOW, deadline)

    def test_schema_validator_is_fail_closed(self):
        root = Path(__file__).resolve().parents[1] / "workflow/schemas"
        plan = dry_run("NLE-WF-GOV-03", "run-1", "tenant-1", NOW,
                       NOW + timedelta(hours=1))
        empty = copy.deepcopy(plan)
        empty["dag"]["nodes"] = []
        empty["dag"]["edges"] = []
        with self.assertRaises(SecurityError):
            validate_document(empty, root / "plan-v1.json")
        date_only = copy.deepcopy(plan)
        date_only["now"] = "2026-11-27"
        with self.assertRaises(SecurityError):
            validate_document(date_only, root / "plan-v1.json")
        with tempfile.TemporaryDirectory() as tmp:
            malformed_type = Path(tmp) / "type.json"
            malformed_type.write_text('{"type":"number"}', encoding="utf-8")
            with self.assertRaises(SecurityError):
                validate_document(1, malformed_type)
            malformed_format = Path(tmp) / "format.json"
            malformed_format.write_text(
                '{"type":"string","format":"email"}', encoding="utf-8"
            )
            with self.assertRaises(SecurityError):
                validate_document("a@example.test", malformed_format)

    def test_context_lock_tamper_is_rejected(self):
        from workflow import __main__ as workflow_cli
        original = workflow_cli._git_blob

        def tampered(path, ref="HEAD"):
            data = original(path, ref)
            if path.endswith("context-lock.json"):
                document = json.loads(data)
                document["implementation_fingerprints_sha256"].pop(
                    next(iter(document["implementation_fingerprints_sha256"]))
                )
                return json.dumps(document).encode("utf-8")
            return data

        with mock.patch.object(workflow_cli, "_git_blob", side_effect=tampered):
            with self.assertRaises(SecurityError):
                workflow_cli.verify_context_lock()

    def test_dag_cycle_is_rejected(self):
        with self.assertRaises(SecurityError):
            validate_dag([{"id": "a"}, {"id": "b"}], [("a", "b"), ("b", "a")])

    def test_c12_accountable_executor_collision_is_blocked(self):
        contract = validate_c12_workflow(load_workflows()["NLE-WF-QNT-05"])
        self.assertIn("ACCOUNTABLE_EXECUTES", contract["segregation_violations"])
        self.assertFalse(contract["execution_allowed"])
        scope = CommandScope(
            actor=COMMAND_SCOPE.actor, tenant_id="tenant-1", project_id="project-1",
            task_id="task-1", workflow_id="NLE-WF-QNT-05",
        )
        with self.assertRaises(SecurityError):
            WorkflowCommands(
                None, scope, policy_sha256=POLICY, policy_epoch=1,
                risk="HIGH_ASSURANCE",
            )

    def test_c12_dispatcher_identity_cannot_be_replaced(self):
        workflow = copy.deepcopy(load_workflows()["NLE-WF-GOV-03"])
        workflow["dispatch_agent"] = "NLE-OTHER"
        with self.assertRaises(SecurityError):
            validate_c12_workflow(workflow)

    def test_retry_429_respects_attempt_cap(self):
        self.assertEqual(retry_decision(429, MAX_ATTEMPTS, retry_after=1), "FAILED")

    def test_schema_files_exist(self):
        root = Path(__file__).resolve().parents[1] / "workflow/schemas"
        for filename in ("event-v1.json", "run-v1.json", "command-v1.json",
                         "plan-v1.json"):
            self.assertTrue((root / filename).is_file())

    def test_produced_documents_validate_against_schemas(self):
        root = Path(__file__).resolve().parents[1] / "workflow/schemas"
        event = make_event()
        validate_document(event.canonical(), root / "event-v1.json")
        contract = RunContract(
            run_id="run-schema", tenant_id="tenant-1", project_id="project-1",
            task_id="task-1", workflow_id="NLE-WF-GOV-03",
            workflow_version="0.1.0", event_id=event.event_id,
            correlation_id=event.correlation_id, state="RECEIVED", revision=0,
            attempts=0, source_lock_sha256=SOURCE_LOCK,
            deadline_at=NOW + timedelta(hours=1), risk="ELEVATED",
            idempotency_key=event.idempotency_key, agent_id="agent-1",
            inputs_ref=event.payload_ref,
        )
        validate_document(contract.document(), root / "run-v1.json")
        plan = dry_run("NLE-WF-GOV-03", "run-1", "tenant-1", NOW,
                       NOW + timedelta(hours=1))
        validate_document(plan, root / "plan-v1.json")
        command_schema = json.loads(
            (root / "command-v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(set(command_schema["required"]),
                         set(command_schema["properties"]))


if __name__ == "__main__":
    unittest.main()
