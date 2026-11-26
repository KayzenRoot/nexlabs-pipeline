"""Tests for the deterministic security regression scan."""
from __future__ import annotations

import contextlib
import io
import unittest

from scripts.security import scan_repository as security_scan


class SecurityScanTests(unittest.TestCase):
    def test_private_key_marker_detected(self):
        marker = "-----BEGIN " + "PRIVATE KEY-----"
        self.assertEqual(security_scan.scan_text(marker)[0][0], "private_key")

    def test_provider_token_detected_without_exposing_value(self):
        token = "ghp_" + ("a" * 36)
        findings = security_scan.scan_text("token=" + token)
        self.assertEqual(findings[0][0], "github_token")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            original = security_scan.scan_repository
            security_scan.scan_repository = lambda root=None: ([], [("x", "github_token", 1)])
            try:
                security_scan.main()
            finally:
                security_scan.scan_repository = original
        self.assertNotIn(token, output.getvalue())
        self.assertIn("SECURITY_FINDING github_token", output.getvalue())

    def test_paperclip_secret_assignment_detected(self):
        assignment = "BETTER_AUTH_SECRET=" + ("f" * 64)
        self.assertEqual(security_scan.scan_text(assignment)[0][0], "paperclip_secret_value")

    def test_runtime_artifacts_are_rejected(self):
        paths = [
            "deploy/local/data/postgres/PG_VERSION",
            "deploy/local/backups/paperclip-data.zip",
            "deploy/local/restore-test-1/file",
            ".env",
            "deploy/local/.env.example",
            "docs/Deployment.md",
        ]
        self.assertEqual(
            security_scan.runtime_artifact_violations(paths),
            [
                "deploy/local/data/postgres/PG_VERSION",
                "deploy/local/backups/paperclip-data.zip",
                "deploy/local/restore-test-1/file",
                ".env",
            ],
        )

    def test_repository_is_clean(self):
        _, findings = security_scan.scan_repository()
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
