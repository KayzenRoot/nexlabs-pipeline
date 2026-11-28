"""Behavioral tests for the recovered NLE-WF-WO-001 offline workflow contract."""
from __future__ import annotations

import copy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import hmac
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from security.approval import HmacSha256TestVerifier, canonical_approval_bytes
from security.contracts import (
    AccessRequest, ApprovalEnvelope, Grant, Principal, SecurityError,
)
from security.core import EXPECTED_POLICY, policy_fingerprint
from workflow.__main__ import main as workflow_main
from workflow.authorization import authorize_workflow
from workflow.contracts import (
    C12_WORKFLOW_IDS, STATES, TRANSITIONS, WorkflowEvent,
    assert_transition, load_workflows, retry_decision, validate_c12,
    validate_c12_workflow, validate_event, validate_workflow_catalog,
)
from workflow.ledger import Ledger

NOW = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)
PAYLOAD = "a" * 64
POLICY = policy_fingerprint(EXPECTED_POLICY)
KEY = b"synthetic-workflow-test-key-never-production"


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


def make_principal():
    return Principal("agent-1", "agent", "tenant-1", "project-1", "host-1", "ACTIVE", 1)


def make_request(risk="STANDARD", **changes):
    values = dict(
        actor=make_principal(), action="workflow.run", target_id="run-1",
        tenant_id="tenant-1", project_id="project-1", task_id="task-1",
        workflow_id="NLE-WF-GOV-03", skill_id="skill-1", host_id="host-1",
        provider_id="provider-local", risk=risk, policy_sha256=POLICY,
        policy_epoch=1, payload_sha256=PAYLOAD, effect="INTERNAL_ONLY",
        requested_spend_usd=Decimal("0"), now=NOW,
    )
    values.update(changes)
    return AccessRequest(**values)


def make_grant(request, **changes):
    values = dict(
        grant_id="grant-1", principal_id=request.actor.principal_id,
        action=request.action, target_id=request.target_id, tenant_id=request.tenant_id,
        project_id=request.project_id, task_id=request.task_id,
        workflow_id=request.workflow_id, skill_id=request.skill_id,
        host_id=request.host_id, provider_id=request.provider_id, risk=request.risk,
        policy_sha256=request.policy_sha256, policy_epoch=request.policy_epoch,
        issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(minutes=5),
        revoked=False, max_spend_usd=Decimal("0"), external_effects="DENY",
    )
    values.update(changes)
    return Grant(**values)


def make_approval(request):
    return ApprovalEnvelope(
        approval_id="approval-1", actor_id=request.actor.principal_id,
        approver_id="human-owner", approver_kind="human", approver_role="OWNER",
        action=request.action, target_id=request.target_id, tenant_id=request.tenant_id,
        project_id=request.project_id, task_id=request.task_id,
        workflow_id=request.workflow_id, skill_id=request.skill_id,
        host_id=request.host_id, provider_id=request.provider_id, risk=request.risk,
        payload_sha256=request.payload_sha256, policy_sha256=request.policy_sha256,
        evidence_refs=("evidence-001",), max_spend_usd=Decimal("0"),
        nonce="0123456789abcdefghijklmnopqrstuv",
        issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(minutes=5),
    )


def sign(envelope):
    return hmac.new(KEY, canonical_approval_bytes(envelope), hashlib.sha256).hexdigest()


SOURCE_LOCK = "a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e"


class TestLedger(Ledger):
    """Storage test adapter; production mutation boundary is WorkflowCommands."""

    def create_run(self, run_id, workflow_id, version, event, now):
        self._create_run(run_id, "tenant-1", "project-1", "task-1", workflow_id,
                         version, event, now, now + timedelta(hours=1), SOURCE_LOCK)

    def append_event(self, event):
        self._append_event(event)

    def run(self, run_id, tenant_id="tenant-1"):
        return super().run(run_id, tenant_id)

    def transition(self, run_id, target, event_id, now, expected_revision=None,
                   lease_owner=None, lease_epoch=None, reconciliation_ref=None):
        current = self.run(run_id)
        revision = current["revision"] if expected_revision is None else expected_revision
        return self._transition(run_id, "tenant-1", target, event_id, now, revision,
                                lease_owner, lease_epoch, reconciliation_ref)

    def claim_lease(self, run_id, owner, now, ttl_seconds=30):
        revision = self.run(run_id)["revision"]
        return self._claim_lease(
            run_id, "tenant-1", owner, now, ttl_seconds, revision,
        )

    def consume(self, nonce, expires_at, now):
        return self._consume(nonce, expires_at, now)

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

    def recover(self, now):
        return self._recover(
            "tenant-1", "project-1", "task-1", "NLE-WF-GOV-03", now,
        )


def advance(ledger, run_id, *targets):
    for target in targets:
        current = ledger.run(run_id)
        lease = {}
        if current["state"] == "RUNNING":
            owner = "test-owner"
            epoch = ledger.claim_lease(run_id, owner, NOW, 30)
            lease = {"lease_owner": owner, "lease_epoch": epoch}
        ledger.transition(run_id, target, None, NOW,
                          expected_revision=current["revision"], **lease)


class EventContractTests(unittest.TestCase):
    def test_event_contract_and_digest_are_deterministic(self):
        event = make_event()
        validate_event(event)
        self.assertEqual(event.digest(), make_event().digest())
        self.assertEqual(event.canonical()["event_id"], "event-1")

    def test_invalid_event_fields_and_unsafe_payload_reference_deny(self):
        for field, value in (
            ("event_type", "unknown.event"),
            ("payload_ref", "https://example.invalid/private"),
            ("risk", "UNKNOWN"),
        ):
            with self.subTest(field=field):
                event = make_event(**{field: value})
                with self.assertRaises(SecurityError):
                    validate_event(event)
        reversed_event = make_event(received_at=NOW - timedelta(seconds=2))
        with self.assertRaises(SecurityError):
            validate_event(reversed_event)


class LedgerPersistenceTests(unittest.TestCase):
    def test_persistence_and_counts_survive_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            event = make_event()
            with TestLedger(path) as ledger:
                ledger.create_run("run-1", "NLE-WF-GOV-03", "0.1.0", event, NOW)
                ledger.transition("run-1", "VALIDATED", event.event_id, NOW)
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.run("run-1")["state"], "VALIDATED")
                self.assertEqual(ledger.counts()["events"], 1)
                self.assertEqual(ledger.integrity(), "ok")

    def test_duplicate_event_is_atomic_and_has_no_second_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                ledger.create_run("run-1", "NLE-WF-GOV-03", "0.1.0", event, NOW)
                with self.assertRaisesRegex(SecurityError, "DUPLICATE_EVENT"):
                    ledger.create_run("run-2", "NLE-WF-GOV-03", "0.1.0", event, NOW)
                self.assertEqual(ledger.counts()["events"], 1)
                self.assertEqual(ledger.counts()["runs"], 1)

    def test_events_are_append_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                ledger.append_event(make_event())
                for statement in (
                    "UPDATE events SET event_type='incident.opened'",
                    "DELETE FROM events",
                ):
                    with self.subTest(statement=statement):
                        with self.assertRaises(sqlite3.DatabaseError):
                            ledger._conn.execute(statement)


class StateMachineTests(unittest.TestCase):
    def test_invalid_transition_is_denied(self):
        with self.assertRaisesRegex(SecurityError, "STATE_TRANSITION_FORBIDDEN"):
            assert_transition("RECEIVED", "RUNNING")

    def test_internal_path_and_terminal_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                ledger.create_run("run-1", "NLE-WF-GOV-03", "0.1.0", event, NOW)
                advance(ledger, "run-1", "VALIDATED", "QUEUED", "RUNNING", "REVIEW",
                        "APPROVED", "VERIFIED", "COMPLETED")
                self.assertEqual(ledger.run("run-1")["state"], "COMPLETED")
                self.assertIn("COMPLETED", STATES)
                with self.assertRaisesRegex(SecurityError, "STATE_TRANSITION_FORBIDDEN"):
                    ledger.transition("run-1", "QUEUED", None, NOW)

    def test_terminal_states_have_no_transitions(self):
        for state in ("COMPLETED", "CANCELLED", "QUARANTINED"):
            with self.subTest(state=state):
                self.assertEqual(TRANSITIONS[state], frozenset())


class NonceAndApprovalTests(unittest.TestCase):
    def test_nonce_is_single_use_across_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            with TestLedger(path) as ledger:
                self.assertTrue(ledger._consume("nonce-1", NOW + timedelta(minutes=1), NOW))
                self.assertFalse(ledger._consume("nonce-1", NOW + timedelta(minutes=1), NOW))
            with TestLedger(path) as ledger:
                self.assertFalse(ledger._consume("nonce-1", NOW + timedelta(minutes=1), NOW))

    def test_high_assurance_approval_replay_is_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            request = make_request("HIGH_ASSURANCE")
            approval = make_approval(request)
            kwargs = dict(
                current_policy_sha256=POLICY, current_policy_epoch=1,
                approval=approval, approval_signature=sign(approval),
                verifier=HmacSha256TestVerifier(KEY),
            )
            with TestLedger(path) as ledger:
                allowed = authorize_workflow(ledger, request, [make_grant(request)], **kwargs)
                self.assertTrue(allowed.allowed)
            with TestLedger(path) as ledger:
                replay = authorize_workflow(ledger, request, [make_grant(request)], **kwargs)
                self.assertFalse(replay.allowed)
                self.assertEqual(replay.reason, "APPROVAL_REPLAY")

    def test_self_approval_is_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            request = make_request("HIGH_ASSURANCE")
            approval = make_approval(request)
            approval = replace(approval, approver_id=request.actor.principal_id)
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                result = authorize_workflow(
                    ledger, request, [make_grant(request)], current_policy_sha256=POLICY,
                    current_policy_epoch=1, approval=approval,
                    approval_signature=sign(approval), verifier=HmacSha256TestVerifier(KEY),
                )
                self.assertEqual(result.reason, "SELF_APPROVAL_FORBIDDEN")


class AuthorizationTests(unittest.TestCase):
    def test_exact_scope_allows_and_unknown_scope_denies(self):
        request = make_request()
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                allowed = authorize_workflow(
                    ledger, request, [make_grant(request)],
                    current_policy_sha256=POLICY, current_policy_epoch=1,
                )
                self.assertTrue(allowed.allowed)
                cross = make_request(tenant_id="tenant-2")
                denied = authorize_workflow(
                    ledger, cross, [make_grant(request)],
                    current_policy_sha256=POLICY, current_policy_epoch=1,
                )
                self.assertEqual(denied.reason, "TENANT_ISOLATION_DENY")

    def test_no_grant_or_nonzero_spend_denies(self):
        request = make_request()
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                no_grant = authorize_workflow(
                    ledger, request, [], current_policy_sha256=POLICY,
                    current_policy_epoch=1,
                )
                self.assertEqual(no_grant.reason, "NO_EXACT_SCOPE_GRANT")
                spend = authorize_workflow(
                    ledger, make_request(requested_spend_usd=Decimal("0.01")),
                    [make_grant(request)], current_policy_sha256=POLICY,
                    current_policy_epoch=1,
                )
                self.assertEqual(spend.reason, "SPEND_FORBIDDEN")


class ConcurrencyAndLeaseTests(unittest.TestCase):
    def test_same_idempotency_has_one_winner_under_threads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.sqlite3"
            with TestLedger(path):
                pass
            barrier = threading.Barrier(8)
            results = []
            lock = threading.Lock()

            def worker():
                ledger = TestLedger(path)
                try:
                    try:
                        barrier.wait(timeout=5)
                    except threading.BrokenBarrierError:
                        outcome = "barrier"
                    else:
                        ledger.create_run("run-1", "NLE-WF-GOV-03", "0.1.0", make_event(), NOW)
                        outcome = "allowed"
                except SecurityError:
                    outcome = "duplicate"
                except sqlite3.Error:
                    outcome = "database-error"
                finally:
                    ledger.close()
                with lock:
                    results.append(outcome)

            threads = [threading.Thread(target=worker) for _ in range(8)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            self.assertEqual(results.count("allowed"), 1)
            self.assertEqual(results.count("duplicate"), 7)
            with TestLedger(path) as ledger:
                self.assertEqual(ledger.counts()["runs"], 1)

    def test_lease_conflict_and_stale_fence_deny(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                ledger.create_run("run-1", "NLE-WF-GOV-03", "0.1.0", event, NOW)
                advance(ledger, "run-1", "VALIDATED", "QUEUED", "RUNNING")
                epoch1 = ledger.claim_lease("run-1", "owner-a", NOW, 30)
                with self.assertRaisesRegex(SecurityError, "LEASE_HELD"):
                    ledger.claim_lease("run-1", "owner-b", NOW, 30)
                epoch2 = ledger.claim_lease("run-1", "owner-a", NOW, 30)
                self.assertGreater(epoch2, epoch1)
                with self.assertRaisesRegex(SecurityError, "RUN_LEASE_FENCE_MISMATCH"):
                    ledger.transition("run-1", "REVIEW", event.event_id, NOW,
                                      lease_owner="owner-a", lease_epoch=epoch1)
                ledger.transition("run-1", "REVIEW", event.event_id, NOW,
                                  lease_owner="owner-a", lease_epoch=epoch2)


class RecoveryTests(unittest.TestCase):
    def test_recovery_marks_retry_and_unknown_effect_without_blind_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                ledger.create_run("run-1", "NLE-WF-GOV-03", "0.1.0", event, NOW)
                advance(ledger, "run-1", "VALIDATED", "QUEUED", "RUNNING")
                ledger.claim_lease("run-1", "owner-a", NOW - timedelta(minutes=2), 1)
                ledger.create_run("run-2", "NLE-WF-GOV-03", "0.1.0",
                                  make_event(event_id="event-2", idempotency_key="idem-2"), NOW)
                advance(ledger, "run-2", "VALIDATED", "QUEUED", "RUNNING", "REVIEW",
                        "APPROVED", "EFFECT_READY", "EFFECT_IN_PROGRESS")
                result = ledger.recover(NOW)
                self.assertEqual(result, {"retry_wait": 1, "unknown_effect": 1, "failed": 0})
                self.assertEqual(ledger.run("run-1")["state"], "RETRY_WAIT")
                self.assertEqual(ledger.run("run-2")["state"], "UNKNOWN_EFFECT")

    def test_outbox_is_unique_and_dlq_keeps_sanitized_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TestLedger(Path(tmp) / "ledger.sqlite3") as ledger:
                event = make_event()
                ledger.create_run("run-1", "NLE-WF-GOV-03", "0.1.0", event, NOW)
                ledger.enqueue_outbox("run-1", event.event_id, "payload-ref-1", NOW)
                with self.assertRaisesRegex(SecurityError, "DUPLICATE_OUTBOX"):
                    ledger.enqueue_outbox("run-1", event.event_id, "payload-ref-1", NOW)
                ledger.dead_letter("run-1", "INTEGRITY_FAILURE", "ref-sanitized", NOW)
                counts = ledger.counts()
                self.assertEqual(counts["outbox"], 1)
                self.assertEqual(counts["dlq"], 1)


class C12AndPolicyTests(unittest.TestCase):
    def test_c12_exact_five_dispatch_only_contracts(self):
        contracts = validate_c12()
        self.assertEqual(set(contracts), set(C12_WORKFLOW_IDS))
        for contract in contracts.values():
            self.assertTrue(contract["dispatch_only"])
            self.assertNotIn(contract["dispatcher"], contract["execution_agents"])
            self.assertEqual(contract["skill_imports"], [])
            self.assertEqual(contract["memory_grants"], [])
            self.assertFalse(contract["client_access"])
            self.assertEqual(contract["activation"], "DISABLED")

    def test_c12_negative_mutations_are_rejected(self):
        base = load_workflows()["NLE-WF-GOV-03"]
        mutations = (
            ("dispatcher_executes", lambda w: w["steps"].append(
                {"agent_id": w["dispatch_agent"], "external_effects": "DENY"})),
            ("dispatcher_reviews", lambda w: w.__setitem__("reviewer", w["dispatch_agent"])),
            ("activation_enabled", lambda w: w.__setitem__("activation", "ENABLED")),
            ("effect_allowed", lambda w: w.__setitem__("effect_policy", "ALLOW")),
            ("spend_nonzero", lambda w: w.__setitem__("new_spend_limit_usd", 1)),
            ("memory_grant", lambda w: w.__setitem__("memory_grants", ["memory-1"])),
            ("memory_grant_case", lambda w: w.__setitem__("Memory_Grants", ["memory-1"])),
            ("memory_grant_singular", lambda w: w.__setitem__("memory_grant", ["memory-1"])),
            ("skill_grant", lambda w: w.__setitem__("skill_grant", ["skill-1"])),
            ("client_permission", lambda w: w.__setitem__("client_permission", True)),
            ("entitlements", lambda w: w.__setitem__("entitlements", ["ent-1"])),
            ("secrets", lambda w: w.__setitem__("secrets", ["secret-1"])),
            ("unknown_field", lambda w: w.__setitem__("foo", "bar")),
            ("step_memory_grant_case",
             lambda w: w["steps"][0].__setitem__("Memory_Grants", ["memory-1"])),
            ("nested_common_tests",
             lambda w: w["common_tests"].append({"grants": ["grant-1"]})),
            ("nested_inputs",
             lambda w: w.__setitem__("inputs", {"client_access": True})),
            ("nested_scenario",
             lambda w: w.__setitem__("scenario_specific_not_run",
                                     {"memory_grants": ["memory-1"]})),
            ("nested_step_task",
             lambda w: w["steps"][0].__setitem__("task", {"grants": ["grant-1"]})),
            ("nested_step_packages",
             lambda w: w["steps"][0]["eligible_packages"].append(
                 {"skill_grant": "skill-1"})),
            ("privileges", lambda w: w.__setitem__("privileges", {"elevated": True})),
            ("step_client_access", lambda w: w["steps"][0].__setitem__("client_access", True)),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                workflow = copy.deepcopy(base)
                mutate(workflow)
                with self.assertRaises(SecurityError):
                    validate_c12_workflow(workflow)

    def test_catalog_rejects_grant_fields_outside_c12(self):
        workflows = [copy.deepcopy(item) for item in load_workflows().values()]
        target = next(item for item in workflows if item["id"] not in C12_WORKFLOW_IDS)
        target["grants"] = ["external-grant"]
        with self.assertRaises(SecurityError):
            validate_workflow_catalog(workflows)

    def test_retry_policy_respects_auth_rate_limit_and_attempt_cap(self):
        self.assertEqual(retry_decision(401, 0), "BLOCK")
        self.assertEqual(retry_decision(403, 0), "BLOCK")
        self.assertEqual(retry_decision(429, 0, retry_after=10), "RETRY_AFTER")
        self.assertEqual(retry_decision(500, 0), "RETRY_WAIT")
        self.assertEqual(retry_decision(500, 1), "FAILED")
        self.assertEqual(retry_decision(429, 1), "FAILED")
        self.assertEqual(retry_decision(500, 2), "FAILED")
        self.assertEqual(retry_decision(404, 0), "FAILED")

    def test_catalog_is_large_and_all_workflows_disabled(self):
        workflows = load_workflows()
        self.assertEqual(len(workflows), 62)
        self.assertTrue(all(item["activation"] == "DISABLED" for item in workflows.values()))


class CliTests(unittest.TestCase):
    def test_verify_cli(self):
        self.assertEqual(workflow_main(["verify"]), 0)

    def test_compile_c12_and_dry_run_validate_integrity(self):
        for command in ("compile", "c12", "dry-run"):
            with self.subTest(command=command):
                self.assertEqual(workflow_main([command]), 0)


if __name__ == "__main__":
    unittest.main()
