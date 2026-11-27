"""Adversarial regression tests for the CD-02 authorization, ledger and recovery corrections."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from security.contracts import Grant, Principal, SecurityError
from security.core import EXPECTED_POLICY, policy_fingerprint
from workflow.commands import WorkflowCommands
from workflow.compiler import compile_catalog, dry_run, validate_dag
from workflow.contracts import (
    MAX_ATTEMPTS, WorkflowEvent, load_workflows, retry_decision, validate_c12_workflow,
)
from workflow.ledger import Ledger
from workflow.migrations import SCHEMA_VERSION

NOW = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)
PAYLOAD = "a" * 64
POLICY = policy_fingerprint(EXPECTED_POLICY)
SOURCE_LOCK = "a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e"


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

    def create_run(self, run_id="run-1", event=None):
        event = event or make_event()
        self._create_run(run_id, "tenant-1", "project-1", "task-1", "NLE-WF-GOV-03",
                         "0.1.0", event, NOW, NOW + timedelta(hours=1), SOURCE_LOCK)
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

    def recover(self):
        return self._recover("tenant-1", NOW)


def grant(action, target="run-1", tenant="tenant-1", risk="STANDARD"):
    return Grant(
        grant_id=f"grant-{action}", principal_id="agent-1", action=action,
        target_id=target, tenant_id=tenant, project_id="project-1", task_id="task-1",
        workflow_id="NLE-WF-GOV-03", skill_id="workflow-skill", host_id="host-1",
        provider_id="provider-local", risk=risk, policy_sha256=POLICY, policy_epoch=1,
        issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(minutes=5),
        revoked=False, max_spend_usd=Decimal("0"), external_effects="DENY",
    )


def commands(ledger, grants):
    return WorkflowCommands(
        ledger, actor=Principal("agent-1", "agent", "tenant-1", "project-1", "host-1",
                                "ACTIVE", 1),
        tenant_id="tenant-1", project_id="project-1", task_id="task-1",
        workflow_id="NLE-WF-GOV-03", policy_sha256=POLICY, policy_epoch=1,
        grants=tuple(grants),
    )


class CommandBoundaryTests(unittest.TestCase):
    def test_mutation_without_grant_is_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                with self.assertRaises(SecurityError):
                    commands(ledger, []).create_run(
                        "run-1", "0.1.0", make_event(), NOW, NOW + timedelta(hours=1)
                    )
                self.assertEqual(ledger.counts()["runs"], 0)

    def test_wrong_tenant_grant_is_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                with self.assertRaises(SecurityError):
                    commands(ledger, [grant("workflow.run.create", tenant="tenant-2")]).create_run(
                        "run-1", "0.1.0", make_event(), NOW, NOW + timedelta(hours=1)
                    )
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

    def test_stale_revision_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                commands(ledger, [grant("workflow.run.create")]).create_run(
                    "run-1", "0.1.0", event, NOW, NOW + timedelta(hours=1)
                )
                with self.assertRaises(SecurityError):
                    commands(ledger, [grant("workflow.run.transition")]).transition(
                        "run-1", "VALIDATED", event.event_id, NOW,
                        expected_revision=99, payload_sha256=PAYLOAD
                    )


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

    def test_idempotency_with_divergent_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                with self.assertRaises(SecurityError):
                    ledger._create_run("run-2", "tenant-1", "project-1", "task-1",
                                       "NLE-WF-GOV-03", "0.1.0",
                                       make_event(event_id="event-2", payload_sha256="b" * 64),
                                       NOW, NOW + timedelta(hours=1), SOURCE_LOCK)
                self.assertEqual(ledger.counts()["events"], 1)

    def test_migration_version_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                self.assertEqual(ledger.schema_version, SCHEMA_VERSION)
                self.assertEqual(ledger.integrity(), "ok")

    def test_idempotency_key_divergence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.create_run()
                with self.assertRaises(SecurityError):
                    ledger._append_event(make_event(event_id="event-2", payload_sha256="b" * 64))


class NonceRecoveryTests(unittest.TestCase):
    def test_expired_and_concurrent_nonce(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            with TestLedger(path) as ledger:
                with self.assertRaises(SecurityError):
                    ledger._consume("expired", NOW - timedelta(seconds=1), NOW)
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
        with self.assertRaises(SecurityError):
            dry_run("unknown", "run-1", "tenant-1", NOW, NOW + timedelta(hours=1))

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


if __name__ == "__main__":
    unittest.main()
