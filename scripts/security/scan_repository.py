#!/usr/bin/env python3
"""Deterministic secret and runtime-artifact scan for NLE-INFRA-WO-001.

Stdlib only. The scan is a focused security regression gate, not a replacement
for CodeQL, SonarCloud or a full secret scanner. It never prints matched values:
only the rule name and location are emitted.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 2 * 1024 * 1024
SKIP_SUFFIXES = {
    ".zip", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".woff",
    ".woff2", ".ttf", ".eot", ".mp4", ".webp", ".gz", ".tar",
}
SECRET_PATTERNS = (
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_\w{36,}|github_pat_\w{50,})\b")),
    ("openai_key", re.compile(r"\bsk-\w{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[\w-]{10,}\b")),
    ("credential_url", re.compile(r"https?://[^/\s:@]+:[^/\s:@]+@")),
    ("paperclip_secret_value", re.compile(
        r"(?:BETTER_AUTH_SECRET|PAPERCLIP_TOOL_ACTION_SIGNING_SECRET)\s*=\s*[0-9a-fA-F]{32,}"
    )),
)
RUNTIME_SEGMENT = re.compile(r"(?:^|/)(?:\.env|data|backups|restore-test-[^/]*)(?:/|$)")


def tracked_files(root: Path = ROOT) -> list[str]:
    """Return repository-relative tracked paths, independent of the CWD."""
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [item for item in completed.stdout.decode("utf-8").split("\0") if item]


def scan_text(text: str) -> list[tuple[str, int]]:
    """Return (rule, line) findings without returning the matched value."""
    findings = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for rule, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append((rule, line_number))
    return findings


def runtime_artifact_violations(paths: list[str]) -> list[str]:
    """Return tracked runtime/secret paths that must not be committed."""
    return [
        path
        for path in paths
        if RUNTIME_SEGMENT.search(path) and not path.endswith(".env.example")
    ]


def scan_repository(root: Path = ROOT) -> tuple[list[str], list[tuple[str, str, int]]]:
    """Scan tracked text files and return (paths, findings)."""
    paths = tracked_files(root)
    findings: list[tuple[str, str, int]] = []
    for path in runtime_artifact_violations(paths):
        findings.append((path, "tracked_runtime_artifact", 0))
    for relative in paths:
        candidate = root / relative
        if candidate.suffix.lower() in SKIP_SUFFIXES:
            continue
        try:
            data = candidate.read_bytes()
        except OSError:
            continue
        if len(data) > MAX_BYTES or b"\0" in data[:4096]:
            continue
        text = data.decode("utf-8", errors="ignore")
        for rule, line in scan_text(text):
            findings.append((relative, rule, line))
    return paths, findings


def main() -> int:
    paths, findings = scan_repository()
    for relative, rule, line in findings:
        location = f"{relative}:{line}" if line else relative
        print(f"SECURITY_FINDING {rule} {location}")
    print(f"SECURITY_SCAN files={len(paths)} findings={len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
