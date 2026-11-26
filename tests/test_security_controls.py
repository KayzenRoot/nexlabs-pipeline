"""High-assurance offline security contract regression tests."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import hmac
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from security.approval import (
    HmacSha256TestVerifier, InMemoryNonceStore, canonical_approval_bytes,
)
from security.authorization import authorize
from security.contracts import (
    AccessRequest, ApprovalEnvelope, Grant, Principal, SecurityError,
)
from security.core import EXPECTED_POLICY, verify_policy
from security.isolation import assert_tenant_match, resolve_workspace_path
from security.network import (
    NetworkPeer, NetworkPolicy, ServiceBinding, validate_network_policy,
)
from security.secrets import SecretRef, validate_secret_ref

NOW = datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)
POLICY = "a" * 64
PAYLOAD = "b" * 64
KEY = b"synthetic-test-key-only-never-production"


def fixture_request(risk="STANDARD"):
    actor = Principal("agent-1", "agent", "tenant-1", "project-1", "host-1", "ACTIVE", 7)
    return AccessRequest(
        actor=actor, action="document.read", target_id="doc-1",
        tenant_id="tenant-1", project_id="project-1", task_id="task-1",
        workflow_id="workflow-1", skill_id="skill-1", host_id="host-1",
        provider_id="provider-local", risk=risk, policy_sha256=POLICY,
        policy_epoch=7, payload_sha256=PAYLOAD, effect="INTERNAL_ONLY",
        requested_spend_usd=Decimal("0"), now=NOW,
    )


def fixture_grant(request=None, **changes):
    request = request or fixture_request()
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


def fixture_approval(request=None, **changes):
    request = request or fixture_request("HIGH_ASSURANCE")
    values = dict(
        approval_id="approval-1", actor_id=request.actor.principal_id,
        approver_id="human-owner", approver_kind="human", action=request.action,
        target_id=request.target_id, tenant_id=request.tenant_id,
        payload_sha256=request.payload_sha256, policy_sha256=request.policy_sha256,
        evidence_refs=("evidence-001",), max_spend_usd=Decimal("0"),
        nonce="0123456789abcdefghijklmnopqrstuv", issued_at=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=5),
    )
    values.update(changes)
    return ApprovalEnvelope(**values)


def sign(envelope):
    return hmac.new(KEY, canonical_approval_bytes(envelope), hashlib.sha256).hexdigest()


class AuthorizationTests(unittest.TestCase):
    def test_exact_internal_grant_allows(self):
        request = fixture_request()
        result = authorize(request, [fixture_grant(request)])
        self.assertTrue(result.allowed)
        self.assertEqual(result.reason, "AUTHORIZED_INTERNAL_ONLY")
        self.assertEqual(result.grant_id, "grant-1")

    def test_each_scope_dimension_is_exact(self):
        request = fixture_request()
        fields = (
            "principal_id", "action", "target_id", "tenant_id", "project_id",
            "task_id", "workflow_id", "skill_id", "host_id", "provider_id",
            "risk", "policy_sha256", "policy_epoch",
        )
        for field in fields:
            with self.subTest(field=field):
                grant = fixture_grant(request)
                changed = {"policy_epoch": 8} if field == "policy_epoch" else {
                    field: "other-" + field
                }
                result = authorize(request, [replace(grant, **changed)])
                self.assertFalse(result.allowed)

    def test_revoked_expired_and_future_grants_deny(self):
        request = fixture_request()
        for grant in (
            fixture_grant(request, revoked=True),
            fixture_grant(request, expires_at=NOW),
            fixture_grant(request, issued_at=NOW + timedelta(seconds=1)),
        ):
            self.assertFalse(authorize(request, [grant]).allowed)

    def test_stale_principal_and_cross_tenant_deny(self):
        request = fixture_request()
        stale = replace(request, actor=replace(request.actor, policy_epoch=6))
        cross = replace(request, tenant_id="tenant-2")
        self.assertEqual(authorize(stale, [fixture_grant(request)]).reason, "PRINCIPAL_POLICY_STALE")
        self.assertEqual(authorize(cross, [fixture_grant(request)]).reason, "TENANT_ISOLATION_DENY")

    def test_project_and_host_mismatch_deny(self):
        request = fixture_request()
        self.assertEqual(authorize(replace(request, project_id="project-2"),
                                   [fixture_grant(request)]).reason, "PROJECT_ISOLATION_DENY")
        self.assertEqual(authorize(replace(request, host_id="host-2"),
                                   [fixture_grant(request)]).reason, "HOST_BINDING_DENY")

    def test_external_effect_and_nonzero_spend_deny(self):
        request = fixture_request()
        self.assertEqual(authorize(replace(request, effect="EXTERNAL"),
                                   [fixture_grant(request)]).reason, "EXTERNAL_EFFECTS_DENY")
        self.assertEqual(authorize(replace(request, requested_spend_usd=Decimal("0.01")),
                                   [fixture_grant(request)]).reason, "SPEND_FORBIDDEN")

    def test_unknown_principal_risk_and_privilege_mutation_deny(self):
        request = fixture_request()
        self.assertFalse(authorize(replace(request, actor=replace(request.actor, state="UNKNOWN")),
                                   [fixture_grant(request)]).allowed)
        self.assertFalse(authorize(replace(request, risk="UNKNOWN"),
                                   [fixture_grant(request)]).allowed)
        self.assertEqual(authorize(replace(request, action="grant.create"),
                                   [fixture_grant(request)]).reason, "PRIVILEGE_MUTATION_DENY")

    def test_no_grant_or_hierarchy_inheritance(self):
        request = fixture_request()
        self.assertFalse(authorize(request, []).allowed)
        child = replace(request, actor=replace(request.actor, principal_id="child-agent"))
        self.assertFalse(authorize(child, [fixture_grant(request)]).allowed)

    def test_high_assurance_requires_bound_independent_approval(self):
        request = fixture_request("HIGH_ASSURANCE")
        envelope = fixture_approval(request)
        result = authorize(request, [fixture_grant(request)], approval=envelope,
                          approval_signature=sign(envelope),
                          verifier=HmacSha256TestVerifier(KEY), nonce_store=InMemoryNonceStore())
        self.assertTrue(result.allowed)

    def test_high_assurance_without_approval_denies(self):
        request = fixture_request("HIGH_ASSURANCE")
        self.assertEqual(authorize(request, [fixture_grant(request)]).reason,
                         "INDEPENDENT_HUMAN_APPROVAL_REQUIRED")

    def test_self_approval_and_nonhuman_approver_deny(self):
        request = fixture_request("HIGH_ASSURANCE")
        for changes in ({"approver_id": request.actor.principal_id},
                        {"approver_kind": "agent"}):
            envelope = fixture_approval(request, **changes)
            result = authorize(request, [fixture_grant(request)], approval=envelope,
                               approval_signature=sign(envelope),
                               verifier=HmacSha256TestVerifier(KEY), nonce_store=InMemoryNonceStore())
            self.assertFalse(result.allowed)

    def test_approval_signature_payload_policy_expiry_and_nonce(self):
        request = fixture_request("HIGH_ASSURANCE")
        verifier = HmacSha256TestVerifier(KEY)
        cases = (
            (fixture_approval(request, payload_sha256="c" * 64), "APPROVAL_PAYLOAD_MISMATCH"),
            (fixture_approval(request, policy_sha256="c" * 64), "APPROVAL_POLICY_MISMATCH"),
            (fixture_approval(request, expires_at=NOW), "APPROVAL_EXPIRED_OR_NOT_YET_VALID"),
            (fixture_approval(request, max_spend_usd=Decimal("0.01")), "APPROVAL_SPEND_FORBIDDEN"),
        )
        for envelope, expected in cases:
            result = authorize(request, [fixture_grant(request)], approval=envelope,
                               approval_signature=sign(envelope), verifier=verifier,
                               nonce_store=InMemoryNonceStore())
            self.assertEqual(result.reason, expected)
        envelope = fixture_approval(request)
        result = authorize(request, [fixture_grant(request)], approval=envelope,
                           approval_signature="0" * 64, verifier=verifier,
                           nonce_store=InMemoryNonceStore())
        self.assertEqual(result.reason, "APPROVAL_SIGNATURE_INVALID")

    def test_approval_nonce_is_single_use(self):
        request = fixture_request("HIGH_ASSURANCE")
        envelope = fixture_approval(request)
        store = InMemoryNonceStore()
        kwargs = dict(approval=envelope, approval_signature=sign(envelope),
                      verifier=HmacSha256TestVerifier(KEY), nonce_store=store)
        self.assertTrue(authorize(request, [fixture_grant(request)], **kwargs).allowed)
        self.assertEqual(authorize(request, [fixture_grant(request)], **kwargs).reason,
                         "APPROVAL_REPLAY")

    def test_approval_verifier_rejects_short_key(self):
        with self.assertRaisesRegex(SecurityError, "APPROVAL_KEY_INVALID"):
            HmacSha256TestVerifier(b"short")


class NetworkPolicyTests(unittest.TestCase):
    def test_private_network_and_loopback_services_are_valid(self):
        policy = NetworkPolicy(
            allowed_cidrs=("10.8.0.0/24", "fd00:1234::/64"),
            peers=(NetworkPeer("peer-a", "10.8.0.2", ("10.8.0.2/32",), "keyref-peer-a"),),
            services=(ServiceBinding("paperclip", "10.8.0.1", 3100, "PRIVATE"),
                      ServiceBinding("local-ui", "127.0.0.1", 3100, "LOOPBACK")),
        )
        validate_network_policy(policy)

    def test_public_default_wildcard_and_invalid_networks_deny(self):
        for cidr in ("8.8.8.0/24", "0.0.0.0/0", "::/0", "10.8.0.1/24", "not-a-cidr"):
            with self.subTest(cidr=cidr), self.assertRaises(SecurityError):
                validate_network_policy(NetworkPolicy(allowed_cidrs=(cidr,)))
        for address in ("0.0.0.0", "::", "8.8.8.8", "fe80::1"):
            with self.subTest(address=address), self.assertRaises(SecurityError):
                validate_network_policy(NetworkPolicy(
                    services=(ServiceBinding("svc", address, 443, "PRIVATE"),)
                ))

    def test_peer_must_be_inside_allowlist(self):
        policy = NetworkPolicy(
            allowed_cidrs=("10.8.0.0/24",),
            peers=(NetworkPeer("peer-a", "10.9.0.2", ("10.8.0.2/32",), "keyref-a"),),
        )
        with self.assertRaisesRegex(SecurityError, "NETWORK_PEER_OUTSIDE_ALLOWLIST"):
            validate_network_policy(policy)

    def test_peer_routes_cannot_escape_allowlist(self):
        policy = NetworkPolicy(
            allowed_cidrs=("10.8.0.0/24",),
            peers=(NetworkPeer("peer-a", "10.8.0.2", ("0.0.0.0/0",), "keyref-a"),),
        )
        with self.assertRaises(SecurityError):
            validate_network_policy(policy)

    def test_duplicate_peer_and_key_reference_deny(self):
        peer = NetworkPeer("peer-a", "10.8.0.2", ("10.8.0.2/32",), "keyref-a")
        for peers in ((peer, peer),
                      (peer, NetworkPeer("peer-b", "10.8.0.3", ("10.8.0.3/32",), "keyref-a"))):
            with self.subTest(peers=peers), self.assertRaises(SecurityError):
                validate_network_policy(NetworkPolicy(allowed_cidrs=("10.8.0.0/24",), peers=peers))

    def test_invalid_ports_and_exposure_mismatch_deny(self):
        for port in (0, -1, 65536, True):
            with self.subTest(port=port), self.assertRaises(SecurityError):
                validate_network_policy(NetworkPolicy(
                    services=(ServiceBinding("svc", "10.8.0.1", port, "PRIVATE"),)
                ))
        with self.assertRaises(SecurityError):
            validate_network_policy(NetworkPolicy(
                services=(ServiceBinding("svc", "127.0.0.1", 3100, "PRIVATE"),)
            ))


class SecretReferenceTests(unittest.TestCase):
    def setUp(self):
        self.ref = SecretRef("ref-paperclip-auth", "windows-os-store", "tenant-1",
                             "project-1", "paperclip-auth", "v1")

    def test_opaque_pinned_scoped_reference_validates(self):
        validate_secret_ref(self.ref, tenant_id="tenant-1", project_id="project-1",
                            allowed_providers=frozenset({"windows-os-store"}),
                            allowed_purposes=frozenset({"paperclip-auth"}))

    def test_unknown_provider_purpose_and_cross_tenant_deny(self):
        args = dict(tenant_id="tenant-1", project_id="project-1",
                    allowed_providers=frozenset({"approved-store"}),
                    allowed_purposes=frozenset({"paperclip-auth"}))
        with self.assertRaisesRegex(SecurityError, "SECRET_PROVIDER_NOT_APPROVED"):
            validate_secret_ref(self.ref, **args)
        with self.assertRaisesRegex(SecurityError, "SECRET_TENANT_MISMATCH"):
            validate_secret_ref(self.ref, **{**args, "allowed_providers": frozenset({"windows-os-store"}),
                                             "tenant_id": "tenant-2"})

    def test_latest_secret_version_denied(self):
        ref = replace(self.ref, version="latest")
        with self.assertRaisesRegex(SecurityError, "SECRET_VERSION_NOT_PINNED"):
            validate_secret_ref(ref, tenant_id="tenant-1", project_id="project-1",
                                allowed_providers=frozenset({"windows-os-store"}),
                                allowed_purposes=frozenset({"paperclip-auth"}))

    def test_secret_purpose_and_project_are_exact(self):
        with self.assertRaises(SecurityError):
            validate_secret_ref(self.ref, tenant_id="tenant-1", project_id="project-2",
                                allowed_providers=frozenset({"windows-os-store"}),
                                allowed_purposes=frozenset({"paperclip-auth"}))
        with self.assertRaises(SecurityError):
            validate_secret_ref(self.ref, tenant_id="tenant-1", project_id="project-1",
                                allowed_providers=frozenset({"windows-os-store"}),
                                allowed_purposes=frozenset({"other-purpose"}))


class WorkspaceIsolationTests(unittest.TestCase):
    def test_tenant_mismatch_denies_without_owner_bypass(self):
        with self.assertRaisesRegex(SecurityError, "TENANT_ISOLATION_DENY"):
            assert_tenant_match("tenant-a", "tenant-b")

    def test_valid_workspace_path_is_contained_and_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tenant-1" / "project-1" / "task-1").mkdir(parents=True)
            result = resolve_workspace_path(root, "tenant-1", "project-1", "task-1", "draft/output.txt")
            self.assertTrue(result.is_relative_to(root.resolve()))
            self.assertFalse(result.exists())

    def test_traversal_absolute_and_windows_paths_deny(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tenant-1" / "project-1" / "task-1").mkdir(parents=True)
            for value in ("../other/file", "/etc/passwd", "C:/secret.txt", "a\\..\\secret"):
                with self.subTest(value=value), self.assertRaises(SecurityError):
                    resolve_workspace_path(root, "tenant-1", "project-1", "task-1", value)

    def test_symlink_component_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "tenant-1" / "project-1" / "task-1"
            base.mkdir(parents=True)
            outside = root / "outside"
            outside.mkdir()
            try:
                (base / "linked").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaisesRegex(SecurityError, "WORKSPACE_LINK_FORBIDDEN"):
                resolve_workspace_path(root, "tenant-1", "project-1", "task-1", "linked/secret.txt")

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_windows_junction_component_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "tenant-1" / "project-1" / "task-1"
            base.mkdir(parents=True)
            outside = root / "outside"
            outside.mkdir()
            junction = base / "junction"
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
                                    capture_output=True)
            if result.returncode != 0:
                self.skipTest("junction creation unavailable")
            try:
                with self.assertRaisesRegex(SecurityError, "WORKSPACE_LINK_FORBIDDEN"):
                    resolve_workspace_path(root, "tenant-1", "project-1", "task-1", "junction/secret.txt")
            finally:
                subprocess.run(["cmd", "/c", "rmdir", str(junction)], capture_output=True)


class PolicyTests(unittest.TestCase):
    def test_canonical_policy_is_valid(self):
        verify_policy(EXPECTED_POLICY)

    def test_policy_mutation_fails_closed(self):
        changed = dict(EXPECTED_POLICY)
        changed["default_effect"] = "ALLOW"
        with self.assertRaisesRegex(SecurityError, "POLICY_DRIFT_OR_GRANT"):
            verify_policy(changed)


if __name__ == "__main__":
    unittest.main()
