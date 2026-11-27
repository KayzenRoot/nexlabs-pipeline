"""Adversarial regression tests for the CD-02 authorization, ledger and recovery corrections."""
from __future__ import annotations

import copy
from dataclasses import fields
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from security.approval import HmacSha256TestVerifier, canonical_approval_bytes
from security.contracts import ApprovalEnvelope, Grant, Principal, SecurityError
from security.core import EXPECTED_POLICY, policy_fingerprint
from workflow.commands import CommandScope, WorkflowCommands, _payload_digest
from workflow.compiler import compile_catalog, dry_run, validate_dag
from workflow.contracts import (
    MAX_ATTEMPTS, RunContract, WorkflowEvent, load_workflows, retry_decision,
    validate_c12_workflow, validate_workflow_catalog,
)
from workflow.ledger import Ledger
from workflow.migrations import MIGRATION_1, MIGRATION_2, SCHEMA_VERSION

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

    def advance(self, run_id, *targets):
        for target in targets:
            current = self.run(run_id)
            lease = {}
            if current["state"] == "RUNNING":
                owner = "owner-a"
                epoch = self._claim_lease(run_id, "tenant-1", owner, NOW, 30)
                lease = {"lease_owner": owner, "lease_epoch": epoch}
            self.transition(run_id, target, None,
                            expected_revision=current["revision"], **lease)

    def recover(self, now=NOW):
        return self._recover("tenant-1", now)


def make_v2_ledger(path, *, partial_v3=False):
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
                 NOW.isoformat(), "{}"),
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
        conn.commit()
    finally:
        conn.close()


def grant(action, target="run-1", tenant="tenant-1", risk="STANDARD"):
    return Grant(
        grant_id=f"grant-{action}", principal_id="agent-1", action=action,
        target_id=target, tenant_id=tenant, project_id="project-1", task_id="task-1",
        workflow_id="NLE-WF-GOV-03", skill_id="workflow-skill", host_id="host-1",
        provider_id="provider-local", risk=risk, policy_sha256=POLICY, policy_epoch=1,
        issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(minutes=5),
        revoked=False, max_spend_usd=Decimal("0"), external_effects="DENY",
    )


COMMAND_SCOPE = CommandScope(
    actor=Principal("agent-1", "agent", "tenant-1", "project-1", "host-1", "ACTIVE", 1),
    tenant_id="tenant-1", project_id="project-1", task_id="task-1",
    workflow_id="NLE-WF-GOV-03",
)


def commands(ledger, grants):
    return WorkflowCommands(
        ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
        grants=tuple(grants),
    )


def create_payload(event, *, deadline=None, policy_epoch=1):
    deadline = deadline or NOW + timedelta(hours=1)
    return _payload_digest(
        "workflow.run.create", event_sha256=event.digest(),
        workflow_version="0.1.0", deadline_at=deadline.isoformat(),
        policy_epoch=policy_epoch,
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
        task_id="task-1", workflow_id="NLE-WF-GOV-03", skill_id="workflow-skill",
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
                    ledger, [grant("workflow.run.create"), grant("workflow.run.transition")]
                ).create_run("run-1", "0.1.0", event, NOW, NOW + timedelta(hours=1))
                commands(
                    ledger, [grant("workflow.run.transition")]
                ).transition("run-1", "VALIDATED", event.event_id, NOW,
                             expected_revision=0, payload_sha256=PAYLOAD)
                self.assertEqual(ledger.run("run-1")["state"], "VALIDATED")

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
                transition = commands(ledger, [grant("workflow.run.transition")])
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
                self.assertEqual(ledger.run("run-1")["approval_id"], "approval-1")
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
                     "workflow_id": "NLE-WF-GOV-03", "risk": "HIGH_ASSURANCE",
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
            payload_ref=approved_event.payload_ref, policy_epoch=1,
        )
        approval, signature = make_approval(
            payload, nonce="outboxnonce0123456789abcdef",
            approval_id="approval-outbox", action="workflow.outbox.enqueue",
            target_id="run-1",
        )
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                commands(ledger, [grant("workflow.run.create")]).create_run(
                    "run-1", "0.1.0", run_event, NOW, NOW + timedelta(hours=1)
                )
                command = WorkflowCommands(
                    ledger, COMMAND_SCOPE, policy_sha256=POLICY, policy_epoch=1,
                    risk="HIGH_ASSURANCE",
                    grants=(grant("workflow.outbox.enqueue", risk="HIGH_ASSURANCE"),),
                    approval=approval, approval_signature=signature,
                    verifier=HmacSha256TestVerifier(APPROVAL_KEY),
                )
                with self.assertRaises(SecurityError):
                    command.enqueue_outbox("run-1", "event-3", "payload-3", NOW)
                self.assertEqual(ledger.counts()["outbox"], 0)

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
                standard = commands(ledger, [grant("workflow.run.transition")])
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
                                           event.payload_ref, NOW)

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
                with self.assertRaises(SecurityError):
                    ledger._enqueue_outbox("run-1", "tenant-1", event.event_id,
                                           event.payload_ref, NOW)
                ledger.transition("run-1", "CANCELLED")
                self.assertEqual(ledger.run("run-1")["state"], "CANCELLED")

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

    def test_outbox_rejects_terminal_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING", "REVIEW",
                               "APPROVED", "VERIFIED", "COMPLETED")
                with self.assertRaises(SecurityError):
                    ledger._enqueue_outbox("run-1", "tenant-1", event.event_id,
                                           event.payload_ref, NOW)

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
                    value = ledger._consume("same", NOW + timedelta(minutes=1), NOW)
                except (SecurityError, sqlite3.Error):
                    value = False
                finally:
                    ledger.close()
                with lock:
                    results.append(value)

            threads = [threading.Thread(target=worker) for _ in range(6)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(results.count(True), 1)

    def test_recovery_releases_lease_and_caps_retries(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING",
                               "RETRY_WAIT", "QUEUED", "RUNNING")
                ledger._claim_lease("run-1", "tenant-1", "owner-a",
                                    NOW - timedelta(minutes=2), 1)
                result = ledger.recover()
                self.assertEqual(result["failed"], 1)
                self.assertEqual(ledger.run("run-1")["state"], "FAILED")
                self.assertIsNone(ledger.run("run-1")["lease_owner"])

    def test_recovery_fails_stale_or_expired_runs_without_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "stale.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
                ledger._set_flags("run-1", "tenant-1", NOW, stale=True)
                result = ledger.recover()
                self.assertEqual(result["failed"], 1)
                self.assertEqual(ledger.run("run-1")["state"], "FAILED")
            with TestLedger(Path(tmp) / "deadline.sqlite3") as ledger:
                ledger.create_run(deadline=NOW + timedelta(seconds=30))
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING")
                result = ledger.recover(NOW + timedelta(minutes=1))
                self.assertEqual(result["failed"], 1)
                self.assertEqual(ledger.run("run-1")["state"], "FAILED")

    def test_effect_in_progress_can_be_claimed_and_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                ledger.advance("run-1", "VALIDATED", "QUEUED", "RUNNING", "REVIEW",
                               "APPROVED", "EFFECT_READY", "EFFECT_IN_PROGRESS")
                epoch = ledger._claim_lease("run-1", "tenant-1", "effect-owner", NOW, 30)
                revision = ledger.run("run-1")["revision"]
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
                ledger._set_flags("run-1", "tenant-1", NOW, revoked=True)
                with self.assertRaises(SecurityError):
                    ledger._set_flags("run-1", "tenant-1", NOW, revoked=False)
                event = make_event(event_id="event-2", idempotency_key="idem-2")
                ledger.create_run("run-2", event=event)
                ledger.advance("run-2", "VALIDATED", "QUEUED", "RUNNING",
                               "RETRY_WAIT", "QUEUED", "RUNNING")
                epoch = ledger._claim_lease("run-2", "tenant-1", "owner-a", NOW, 30)
                revision = ledger.run("run-2")["revision"]
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


class CompilerAndC12Tests(unittest.TestCase):
    def test_compiler_and_dry_run_are_deterministic(self):
        first = compile_catalog()
        second = compile_catalog()
        self.assertEqual(first, second)
        self.assertEqual(first["summary"]["workflows"], 62)
        self.assertEqual(first["summary"]["grants"], 0)
        plan = dry_run("NLE-WF-GOV-03", "run-1", "tenant-1", NOW, NOW + timedelta(hours=1))
        self.assertFalse(plan["execution_allowed"])
        deadline = NOW + timedelta(hours=1)
        with self.assertRaises(SecurityError):
            dry_run("unknown", "run-1", "tenant-1", NOW, deadline)

    def test_dag_cycle_is_rejected(self):
        with self.assertRaises(SecurityError):
            validate_dag([{"id": "a"}, {"id": "b"}], [("a", "b"), ("b", "a")])

    def test_c12_dispatcher_identity_cannot_be_replaced(self):
        workflow = copy.deepcopy(load_workflows()["NLE-WF-GOV-03"])
        workflow["dispatch_agent"] = "NLE-OTHER"
        with self.assertRaises(SecurityError):
            validate_c12_workflow(workflow)

    def test_retry_429_respects_attempt_cap(self):
        self.assertEqual(retry_decision(429, MAX_ATTEMPTS, retry_after=1), "FAILED")

    def test_schema_files_exist(self):
        root = Path(__file__).resolve().parents[1] / "workflow/schemas"
        for filename in ("event-v1.json", "run-v1.json", "command-v1.json"):
            self.assertTrue((root / filename).is_file())

    def test_schema_required_fields_match_contracts(self):
        root = Path(__file__).resolve().parents[1] / "workflow/schemas"
        event_schema = json.loads((root / "event-v1.json").read_text(encoding="utf-8"))
        run_schema = json.loads((root / "run-v1.json").read_text(encoding="utf-8"))
        command_schema = json.loads(
            (root / "command-v1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(set(event_schema["required"]),
                         {field.name for field in fields(WorkflowEvent)})
        self.assertEqual(set(run_schema["required"]),
                         {field.name for field in fields(RunContract)})
        self.assertEqual(set(command_schema["required"]),
                         set(command_schema["properties"]))


if __name__ == "__main__":
    unittest.main()
