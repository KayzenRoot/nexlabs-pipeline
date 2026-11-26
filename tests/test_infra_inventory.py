"""Static safety and syntax checks for NLE-INFRA-WO-001 inventory collectors."""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
VPS_SCRIPT = ROOT / "scripts" / "infra" / "collect_vps_inventory.sh"
WINDOWS_SCRIPT = ROOT / "scripts" / "infra" / "collect_windows_inventory.ps1"

MUTATING_PATTERNS = [
    r"\bapt(?:-get)?\s+install\b",
    r"\bdocker\s+(?:compose\s+up|run|build|pull|push|rm|stop|start)\b",
    r"\bsystemctl\s+(?:start|stop|restart|enable|disable)\b",
    r"\bufw\s+(?:allow|deny|enable|disable)\b",
    r"\bwg\s+set\b",
    r"\bssh-keygen\b",
    r"\bwsl\s+--install\b",
    r"\b(?:Start|Stop|Restart)-Service\b",
    r"\b(?:Set|New)-NetFirewallRule\b",
    r"\b(?:Remove|Set|Add|Clear)-Item\b",
    r"\b(?:Set|Add)-Content\b",
    r"\bOut-File\b",
    r"\bExport-(?:Csv|Clixml)\b",
    r"\bInvoke-WebRequest\b",
    r"\bInvoke-RestMethod\b",
    r"\bcurl\s+-[fsS]\b",
    r"\bwget\b",
    r"\b(?:iptables|nft)\s+(?:-A|-I|add)\b",
    r"\bsed\s+-i\b",
]

SECRET_ACCESS_PATTERNS = [
    r"\bdocker\s+inspect\b",
    r"\bprintenv\b",
    r"\bGet-ChildItem\s+Env:",
    r"/proc/.*/environ",
    r"\.env\b",
    r"\bauthorized_keys\b",
    r"\bid_(?:rsa|ed25519)\b",
    r"\bhistory\b",
    r"\b(?:ANTHROPIC|OPENAI|GITHUB|PAPERCLIP)_API_KEY\b",
]

class InfraInventorySafetyTests(unittest.TestCase):
    def test_collectors_exist(self):
        self.assertTrue(VPS_SCRIPT.is_file())
        self.assertTrue(WINDOWS_SCRIPT.is_file())

    def test_vps_script_has_valid_bash_syntax(self):
        if not shutil.which("bash"):
            self.skipTest("bash unavailable")
        result = subprocess.run(
            ["bash", "-n", VPS_SCRIPT.relative_to(ROOT).as_posix()],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_collectors_are_explicitly_read_only(self):
        self.assertIn("READ_ONLY", VPS_SCRIPT.read_text(encoding="utf-8"))
        self.assertIn("READ_ONLY", WINDOWS_SCRIPT.read_text(encoding="utf-8"))

    def test_vps_collector_does_not_emit_hostname_or_mac_address(self):
        source = VPS_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("uname -srm", source)
        self.assertNotIn("uname -a", source)
        self.assertIn("network_interface_names", source)
        self.assertNotIn("ip -brief link", source)

    def test_no_mutating_commands(self):
        for path in (VPS_SCRIPT, WINDOWS_SCRIPT):
            source = path.read_text(encoding="utf-8")
            for pattern in MUTATING_PATTERNS:
                with self.subTest(path=path.name, pattern=pattern):
                    self.assertIsNone(re.search(pattern, source, re.IGNORECASE), pattern)

    def test_no_secret_sources_or_raw_environment_capture(self):
        for path in (VPS_SCRIPT, WINDOWS_SCRIPT):
            source = path.read_text(encoding="utf-8")
            for pattern in SECRET_ACCESS_PATTERNS:
                with self.subTest(path=path.name, pattern=pattern):
                    self.assertIsNone(re.search(pattern, source, re.IGNORECASE), pattern)

    def test_codex_login_output_is_reduced_to_status(self):
        source = WINDOWS_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("codexLoginStatus", source)
        self.assertNotIn("loginOutput", source.split("$report =", 1)[1])

    def test_container_and_listener_addresses_are_redacted(self):
        vps = VPS_SCRIPT.read_text(encoding="utf-8")
        windows = WINDOWS_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("[IPv4]", vps)
        self.assertIn("[IPv6]", vps)
        self.assertIn("[IPv4]", windows)
        self.assertIn("BindScope", windows)

if __name__ == "__main__":
    unittest.main()
