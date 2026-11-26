"""Static deployment contract tests for NLE-INFRA-WO-001/CD-02.

These tests are stdlib-only and safe on Linux CI. They do not require Docker,
PowerShell, network or secrets. Runtime container tests are executed separately
on the Windows host when Docker Desktop is available.
"""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
DEPLOY = ROOT / "deploy"
SCRIPTS = ROOT / "scripts" / "windows"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class DeployContractTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_image_lock_pins_official_paperclip(self):
        lock = json.loads((DEPLOY / "image-lock.json").read_text(encoding="utf-8"))
        paperclip = lock["paperclip"]
        self.assertEqual(paperclip["tag"], "2026.1117.0")
        self.assertTrue(HEX64.match(paperclip["index_digest"].removeprefix("sha256:")))
        self.assertEqual(
            paperclip["image"],
            "ghcr.io/paperclipai/paperclip:2026.1117.0@" + paperclip["index_digest"],
        )
        self.assertIn("linux/amd64", paperclip["platforms"])
        self.assertIn("linux/arm64", paperclip["platforms"])
        self.assertNotIn("-cloud", paperclip["image"])

    def test_image_lock_pins_postgres(self):
        lock = json.loads((DEPLOY / "image-lock.json").read_text(encoding="utf-8"))
        postgres = lock["postgres"]
        self.assertEqual(postgres["tag"], "17-alpine")
        self.assertEqual(
            postgres["image"],
            "postgres:17-alpine@" + postgres["index_digest"],
        )
        self.assertIn("linux/amd64", postgres["platforms"])
        self.assertIn("linux/arm64", postgres["platforms"])

    def test_base_compose_uses_locked_image_and_healthcheck(self):
        lock = json.loads((DEPLOY / "image-lock.json").read_text(encoding="utf-8"))
        text = self.read("deploy/compose.yaml")
        self.assertIn(lock["paperclip"]["image"], text)
        self.assertIn("/api/health", text)
        self.assertIn("BETTER_AUTH_SECRET", text)
        self.assertIn("PAPERCLIP_TOOL_ACTION_SIGNING_SECRET", text)
        self.assertNotIn(":latest", text)
        self.assertNotRegex(text, r"0\.0\.0\.0:\d")
        self.assertIn('HOST: "0.0.0.0"', text)
        self.assertNotIn("-cloud", text)

    def test_local_override_is_loopback_only_and_persistent(self):
        text = self.read("deploy/local/compose.yaml")
        self.assertIn("127.0.0.1:${PAPERCLIP_PORT:-3100}:3100", text)
        self.assertIn("/paperclip", text)
        self.assertNotIn("0.0.0.0", text)
        self.assertNotIn(":latest", text)

    def test_vps_override_uses_external_pinned_postgres_without_public_bind(self):
        lock = json.loads((DEPLOY / "image-lock.json").read_text(encoding="utf-8"))
        text = self.read("deploy/vps/compose.yaml")
        self.assertIn(lock["postgres"]["image"], text)
        self.assertIn("DATABASE_URL", text)
        self.assertIn("127.0.0.1:${PAPERCLIP_PORT:-3100}:3100", text)
        self.assertNotIn("0.0.0.0", text)
        self.assertNotIn(":latest", text)

    def test_powershell_scripts_have_no_destructive_teardown(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SCRIPTS.glob("*.ps1")
            if path.name != "Test-PaperclipDeployment.ps1"
        )
        self.assertNotRegex(combined, r"(?i)docker\s+compose[^\n]*\bdown\b")
        self.assertNotRegex(combined, r"(?i)\bdown\s+(?:-v|--volumes)\b")
        self.assertNotRegex(combined, r"(?i)docker\s+system\s+prune")
        self.assertNotRegex(combined, r"(?i)--force-recreate")

    def test_stop_script_is_graceful(self):
        text = self.read("scripts/windows/Stop-Paperclip.ps1")
        self.assertIn("@('stop')", text)
        self.assertNotIn("@('down')", text)

    def test_restore_isolation_guard_precedes_extraction(self):
        restore = self.read("scripts/windows/Restore-Paperclip.ps1")
        common = self.read("scripts/windows/Paperclip.Common.ps1")
        self.assertIn("RESTORE_FORCE_FORBIDDEN", restore)
        self.assertLess(
            restore.index("Assert-PaperclipIsolatedRestoreTarget -Root"),
            restore.index("Expand-PaperclipBackupArchive -ArchivePath"),
        )
        for marker in (
            "RESTORE_TARGET_NOT_DIRECT_CHILD",
            "RESTORE_TARGET_NOT_ISOLATED",
            "RESTORE_ROOT_REPARSE_POINT",
            "RESTORE_TARGET_ALREADY_EXISTS",
            "RESTORE_FORCE_FORBIDDEN",
        ):
            self.assertIn(marker, common)
        self.assertNotIn("-DestinationPath $TargetDir -Force", common)
        self.assertLess(
            common.index("Set-OwnerOnlyAcl -Path $TargetDir"),
            common.index("Expand-Archive -LiteralPath $ArchivePath"),
        )

    def test_no_secret_values_committed(self):
        patterns = (
            re.compile(r"BETTER_AUTH_SECRET=[0-9a-fA-F]{64}"),
            re.compile(r"PAPERCLIP_TOOL_ACTION_SIGNING_SECRET=[0-9a-fA-F]{64}"),
        )
        for path in list(DEPLOY.rglob("*")) + list(SCRIPTS.glob("*.ps1")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in patterns:
                self.assertIsNone(pattern.search(text), path)

    def test_gitignore_protects_runtime_artifacts(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for entry in (
            ".env",
            "deploy/**/data/",
            "deploy/**/backups/",
            "deploy/**/restore-test-*/",
            "deploy/**/*.zip",
        ):
            self.assertIn(entry, text)

    def test_operational_documentation_covers_required_topics(self):
        text = self.read("deploy/README.md")
        for term in (
            "Docker Desktop",
            "WSL2",
            "127.0.0.1",
            "3100",
            "BETTER_AUTH_SECRET",
            "PAPERCLIP_TOOL_ACTION_SIGNING_SECRET",
            "Backup",
            "Restore",
            "Codex",
            "VPS",
            "105 agents",
        ):
            self.assertIn(term, text)

    def test_compose_yaml_parses_when_pyyaml_is_available(self):
        try:
            import yaml  # type: ignore
        except ImportError:
            self.skipTest("PyYAML not installed; CI runs text contract tests")
        for relative in (
            "deploy/compose.yaml",
            "deploy/local/compose.yaml",
            "deploy/vps/compose.yaml",
        ):
            with self.subTest(path=relative):
                data = yaml.safe_load(self.read(relative))
                self.assertIsInstance(data, dict)
                self.assertIn("services", data)


if __name__ == "__main__":
    unittest.main()
