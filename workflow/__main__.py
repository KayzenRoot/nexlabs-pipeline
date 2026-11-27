"""Deterministic offline verification CLI for the workflow contract."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from scripts.validate_sources import validate as validate_source_pack
from security.contracts import Grant, Principal, require
from security.core import EXPECTED_POLICY, policy_fingerprint
from workflow.commands import WorkflowCommands

from .compiler import compile_catalog, dry_run
from .contracts import (
    ROOT, WorkflowEvent, canonical_bytes, load_workflows, validate_c12,
)
from .ledger import Ledger

SOURCE_LOCK_SHA256 = "a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e"
PAYLOAD = "a" * 64
NOW = datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc)


def _git_blob(path: str, ref: str = "HEAD") -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{ref}:{path}"],
        capture_output=True, check=False,
    )
    require(completed.returncode == 0, "SOURCE_GIT_OBJECT_UNAVAILABLE")
    return completed.stdout


def verify_source_lock() -> None:
    """Validate canonical bytes from Git, independent of checkout line endings."""
    lock_bytes = _git_blob("locks/source-lock.json")
    require(hashlib.sha256(lock_bytes).hexdigest() == SOURCE_LOCK_SHA256,
            "BASELINE_LOCK_DRIFT")
    files = json.loads(lock_bytes.decode("utf-8"))["files"]
    require(len(files) == 364, "BASELINE_SOURCE_COUNT")
    paths = sorted(files)
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "--batch"],
        input=("".join("HEAD:" + path + "\n" for path in paths)).encode("utf-8"),
        capture_output=True, check=False,
    )
    require(completed.returncode == 0, "SOURCE_GIT_OBJECT_UNAVAILABLE")
    output = completed.stdout
    offset = 0
    for relative in paths:
        header_end = output.find(b"\n", offset)
        require(header_end >= 0, "SOURCE_GIT_OBJECT_UNAVAILABLE")
        header = output[offset:header_end].split()
        require(len(header) == 3 and header[1] == b"blob", "SOURCE_GIT_OBJECT_UNAVAILABLE")
        size = int(header[2])
        data_start = header_end + 1
        data = output[data_start:data_start + size]
        require(len(data) == size, "SOURCE_GIT_OBJECT_UNAVAILABLE")
        require(hashlib.sha256(data).hexdigest() == files[relative],
                "SOURCE_FINGERPRINT_MISMATCH")
        offset = data_start + size + 1
    # The established archive/cross-plan validator is byte-exact and runs on Linux.
    if sys.platform != "win32":
        validate_source_pack(ROOT, verbose=False)


def _git_hash_blob(data: bytes) -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "hash-object", "--stdin"],
        input=data, capture_output=True, check=False,
    )
    require(completed.returncode == 0, "SOURCE_GIT_OBJECT_UNAVAILABLE")
    return completed.stdout.decode("ascii").strip()


def _git_ok(*args: str) -> bool:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, check=False).returncode == 0


def verify_context_lock() -> None:
    document = json.loads(_git_blob("locks/NLE-WF-WO-001-context-lock.json").decode("utf-8"))
    base = document["base_sha"]
    require(_git_ok("merge-base", "--is-ancestor", base, "HEAD"),
            "CONTEXT_LOCK_BASE_NOT_ANCESTOR")
    require(_git_ok("diff", "--quiet", "HEAD", "--", "sources"),
            "CONTEXT_LOCK_WORKTREE_SOURCE_DRIFT")
    main_ref = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "origin/main"],
                              capture_output=True, check=False)
    if main_ref.returncode == 0:
        require(main_ref.stdout.decode("utf-8").strip() == base,
                "CONTEXT_LOCK_MAIN_STALE")
    require(len(document["canonical_fingerprints_sha256"]) == 24
            and len(document["implementation_fingerprints_sha256"]) == 17,
            "CONTEXT_LOCK_REQUIRED_SET_INCOMPLETE")
    base_tree = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", f"{base}^{{tree}}"],
        capture_output=True, check=False,
    )
    require(base_tree.returncode == 0, "CONTEXT_LOCK_BASE_UNAVAILABLE")
    require(base_tree.stdout.decode("utf-8").strip() == document["base_tree_sha"],
            "CONTEXT_LOCK_BASE_TREE_MISMATCH")
    require(document["source_pack_files"] == 364, "CONTEXT_LOCK_SOURCE_COUNT")
    for relative, expected in document["canonical_fingerprints_sha256"].items():
        data = _git_blob(relative, base)
        require(hashlib.sha256(data).hexdigest() == expected,
                "CONTEXT_LOCK_CANONICAL_MISMATCH")
        require(_git_hash_blob(data) == document["canonical_git_blob_fingerprints"][relative],
                "CONTEXT_LOCK_CANONICAL_BLOB_MISMATCH")
    for relative, expected in document["implementation_fingerprints_sha256"].items():
        data = _git_blob(relative)
        require(hashlib.sha256(data).hexdigest() == expected,
                "CONTEXT_LOCK_IMPLEMENTATION_MISMATCH")
        require(_git_hash_blob(data) == document["implementation_git_blob_fingerprints"][relative],
                "CONTEXT_LOCK_IMPLEMENTATION_BLOB_MISMATCH")


def _verification_commands(ledger: Ledger) -> WorkflowCommands:
    actor = Principal("verify-agent", "agent", "tenant-1", "project-1", "host-1", "ACTIVE", 1)
    policy = policy_fingerprint(EXPECTED_POLICY)
    common = dict(
        principal_id="verify-agent", target_id="run-verify-1", tenant_id="tenant-1",
        project_id="project-1", task_id="task-1", workflow_id="NLE-WF-GOV-03",
        skill_id="workflow-skill", host_id="host-1", provider_id="provider-local",
        risk="STANDARD", policy_sha256=policy, policy_epoch=1,
        issued_at=NOW - timedelta(minutes=1), expires_at=NOW + timedelta(hours=1),
        revoked=False, max_spend_usd=0, external_effects="DENY",
    )
    grants = (
        Grant(grant_id="verify-create", action="workflow.run.create", **common),
        Grant(grant_id="verify-transition", action="workflow.run.transition", **common),
    )
    return WorkflowCommands(
        ledger, actor=actor, tenant_id="tenant-1", project_id="project-1",
        task_id="task-1", workflow_id="NLE-WF-GOV-03", policy_sha256=policy,
        policy_epoch=1, grants=grants,
    )


def verify() -> dict:
    verify_source_lock()
    verify_context_lock()
    workflows = load_workflows()
    contracts = validate_c12()
    require(len(workflows) == 62 and len(contracts) == 5, "C12_CATALOG_DRIFT")
    catalog = compile_catalog()
    require(catalog["summary"]["workflows"] == 62, "COMPILER_CATALOG_DRIFT")
    dry_run("NLE-WF-GOV-03", "run-verify-1", "tenant-1", NOW, NOW + timedelta(hours=1))
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "workflow-ledger.sqlite3"
        event = WorkflowEvent(
            event_id="event-verify-1", event_type="work_order.ready",
            occurred_at=NOW - timedelta(seconds=1), received_at=NOW,
            producer="offline-verifier", subject_ref="work-order-1",
            tenant_id="tenant-1", correlation_id="corr-1",
            idempotency_key="idem-verify-1", payload_ref="payload-ref-1",
            payload_sha256=PAYLOAD, data_classification="INTERNAL", risk="STANDARD",
        )
        with Ledger(db) as ledger:
            commands = _verification_commands(ledger)
            commands.create_run("run-verify-1", "0.1.0", event, NOW,
                                NOW + timedelta(hours=1))
            commands.transition("run-verify-1", "VALIDATED", event.event_id, NOW,
                                expected_revision=0, payload_sha256=PAYLOAD)
            ledger.integrity()
        with Ledger(db) as ledger:
            counts = ledger.counts()
            require(counts["events"] == 1 and counts["runs"] == 1,
                    "PERSISTENCE_VERIFY_FAILED")
            ledger.integrity()
    return {"workflows": len(workflows), "c12": len(contracts),
            "events": 1, "runs": 1, "nonces": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="validate source lock, Context Lock, C12 and ledger smoke test")
    commands.add_parser("c12", help="emit the five dispatch-only C12 contracts")
    commands.add_parser("compile", help="compile the deterministic 62-workflow catalog")
    dry = commands.add_parser("dry-run", help="compile a deterministic per-run DAG without effects")
    dry.add_argument("--workflow", default="NLE-WF-GOV-03")
    dry.add_argument("--tenant", default="tenant-1")
    dry.add_argument("--run-id", default="dry-run-1")
    args = parser.parse_args(argv)
    try:
        if args.command == "c12":
            sys.stdout.buffer.write(canonical_bytes(validate_c12()))
        elif args.command == "compile":
            sys.stdout.buffer.write(canonical_bytes(compile_catalog()))
        elif args.command == "dry-run":
            sys.stdout.buffer.write(canonical_bytes(
                dry_run(args.workflow, args.run_id, args.tenant, NOW,
                        NOW + timedelta(hours=1))
            ))
        else:
            result = verify()
            print("WORKFLOW_OK workflows=%(workflows)d c12=%(c12)d events=%(events)d "
                  "runs=%(runs)d nonces=%(nonces)d" % result)
    except (OSError, ValueError, TypeError, KeyError, AssertionError) as exc:
        print("WORKFLOW_REJECTED " + type(exc).__name__ + ":" + str(exc),
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
