"""Behavioral regression tests for the offline registry compiler."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from registry.core import (
    CEO, EXPECTED_POLICY, RegistryError, ROOT, SOURCE_LOCK, build,
    canonical_bytes, index, provision_plan, read_json, safe_path, sha256,
    validate_dependencies, verify_document, verify_policy,
)


class RegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = build()
        cls.plan = provision_plan(bundle=cls.bundle)

    def test_counts_and_references(self):
        b = self.bundle
        self.assertEqual(len(b["manifests"]), 92)
        self.assertEqual(len(b["agent_locks"]), 105)
        self.assertEqual(len(b["competencies"]), 1071)
        self.assertEqual(len(b["assignments"]), 1110)
        self.assertEqual(len(b["shared_core_baseline"]), 8)
        self.assertEqual(len(b["quarantine"]), 18)
        ids = {row["assignment_id"] for row in b["assignments"]}
        self.assertEqual(len(ids), 1110)
        self.assertEqual(ids, {i for lock in b["agent_locks"].values()
                               for i in lock["assignment_ids"]})
        self.assertEqual(ids, {i for pkg in b["manifests"].values()
                               for i in pkg["assignment_ids"]})

    def test_lock_hashes_recompute_and_match_specs(self):
        for aid, lock in self.bundle["agent_locks"].items():
            payload = {k: v for k, v in lock.items() if k != "lock_sha256"}
            self.assertEqual(sha256(canonical_bytes(payload)), lock["lock_sha256"], aid)
            for ref in lock["package_specs"]:
                manifest = self.bundle["manifests"][ref["package_id"]]
                self.assertEqual(ref["spec_sha256"], manifest["spec_sha256"])
                self.assertEqual(ref["spec_sha256"],
                                 sha256(safe_path(ROOT, manifest["spec_path"]).read_bytes()))
                self.assertIsNone(ref["artifact_sha256"])

    def test_no_implicit_grants(self):
        for entry in list(self.bundle["agent_locks"].values()) + list(self.bundle["manifests"].values()):
            self.assertEqual(entry["tool_grants"], [])
            self.assertEqual(entry["credential_grants"], [])
            self.assertFalse(entry.get("enabled", False))
            self.assertFalse(entry.get("execution_allowed", False))
        for source in self.bundle["quarantine"]:
            self.assertFalse(source["download_allowed"])
            self.assertFalse(source["execution_allowed"])
            self.assertFalse(source["artifact_license_verified"])
            self.assertIsNone(source["commit_sha"])
        self.assertEqual(sum(q["state"] == "QUARANTINED" for q in self.bundle["quarantine"]), 17)

    def test_topological_plan_and_ceo_reconciliation(self):
        intents = self.plan["agent_intents"]
        self.assertEqual(len(intents), 105)
        self.assertEqual(intents[0]["canonical_id"], CEO)
        self.assertEqual(intents[0]["intent"], "RECONCILE_EXISTING_BEFORE_CREATE")
        seen = set()
        for intent in intents:
            parent = intent["reports_to"]
            self.assertTrue(parent is None or parent in seen)
            self.assertNotIn(intent["canonical_id"], seen)
            seen.add(intent["canonical_id"])
            self.assertIsNone(intent["runtime_id"])
            self.assertIsNone(intent["model_id"])
            self.assertIsNone(intent["adapter"])
            self.assertFalse(intent["enabled"])
            self.assertFalse(intent["heartbeat_enabled"])
            self.assertFalse(intent["runtime_match_verified"])
            self.assertEqual(intent["skill_imports"], [])
            self.assertEqual(intent["credential_grants"], [])
            self.assertEqual(intent["tool_grants"], [])
            self.assertEqual(intent["external_effects"], "DENY")
            self.assertEqual(intent["max_additional_spend_usd"], 0)
        self.assertEqual(len([a for a in intents if a["independent_escalation_to_owner"]]), 8)
        self.assertEqual(self.plan["actual_creates"], 0)
        self.assertEqual(self.plan["actual_updates"], 0)
        self.assertEqual(self.plan["actual_model_calls"], 0)

    def test_determinism(self):
        self.assertEqual(canonical_bytes(self.bundle), canonical_bytes(build()))
        self.assertEqual(canonical_bytes(self.plan), canonical_bytes(provision_plan()))

    def test_exact_document_verification(self):
        self.assertTrue(verify_document(self.bundle))
        self.assertTrue(verify_document(self.plan))

    def test_tampered_manifest_is_rejected(self):
        changed = copy.deepcopy(self.bundle)
        changed["manifests"]["executive-strategy"]["tool_grants"] = ["unapproved"]
        with self.assertRaises(RegistryError):
            verify_document(changed)

    def test_tampered_lock_is_rejected(self):
        changed = copy.deepcopy(self.bundle)
        changed["agent_locks"][CEO]["lock_sha256"] = "0" * 64
        with self.assertRaises(RegistryError):
            provision_plan(bundle=changed)

    def test_tampered_plan_is_rejected(self):
        changed = copy.deepcopy(self.plan)
        changed["agent_intents"][0]["enabled"] = True
        with self.assertRaises(RegistryError):
            verify_document(changed)

    def test_unknown_fields_and_type_coercion_rejected(self):
        for field, value in [("apply", True), ("actual_creates", False)]:
            changed = copy.deepcopy(self.plan)
            changed[field] = value
            with self.subTest(field=field), self.assertRaises(RegistryError):
                verify_document(changed)

    def test_policy_cannot_grant_network(self):
        policy = copy.deepcopy(EXPECTED_POLICY)
        policy["allow_network"] = True
        with self.assertRaises(RegistryError):
            verify_policy(policy)

    def test_dependency_cycles_and_dangling_ids(self):
        for packages in (
            {"a": {"dependencies": ["b"]}, "b": {"dependencies": ["a"]}},
            {"a": {"dependencies": ["missing"]}},
            {"a": {"dependencies": []}, "b": {"dependencies": ["a", "a"]}},
        ):
            with self.subTest(packages=packages), self.assertRaises(RegistryError):
                validate_dependencies(packages)
        validate_dependencies({"a": {"dependencies": []}, "b": {"dependencies": ["a"]}})

    def test_duplicate_identifiers_and_json_keys(self):
        with self.assertRaises(RegistryError):
            index([{"id": "x"}, {"id": "x"}], "id")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "candidate.json"
            p.write_text('{"enabled":false,"enabled":true}', encoding="utf-8")
            with self.assertRaises(RegistryError):
                read_json(p)
            p.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaises(RegistryError):
                read_json(p)

    def test_source_lock_tampering_rejected_before_reading_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = root / SOURCE_LOCK
            p.parent.mkdir()
            p.write_bytes(b"{}")
            with self.assertRaisesRegex(RegistryError, "BASELINE_LOCK_DRIFT"):
                build(root)

    def test_path_traversal_and_link_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for p in ("../outside", "/outside", "C:/outside", "a\\b", "a/../b"):
                with self.subTest(path=p), self.assertRaises(RegistryError):
                    safe_path(root, p)
            target = root / "regular"
            target.write_text("fixture", encoding="utf-8")
            try:
                (root / "linked").symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable on test host")
            with self.assertRaisesRegex(RegistryError, "SOURCE_LINK_FORBIDDEN"):
                safe_path(root, "linked")

    def test_schema_envelopes_match_compiled_documents(self):
        for filename, document in (
            ("registry-v1.json", self.bundle), ("provision-plan-v1.json", self.plan),
        ):
            schema = read_json(ROOT / "registry/schemas" / filename)
            self.assertEqual(set(schema["required"]), set(document))
            self.assertEqual(set(schema["properties"]), set(document))
            self.assertFalse(schema["additionalProperties"])


if __name__ == "__main__":
    unittest.main()
