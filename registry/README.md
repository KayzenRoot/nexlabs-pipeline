# Offline Skills Registry — NLE-SR-WO-001

From the repository root, using Python 3.10+ and no dependencies:

    python -m registry verify
    python -m registry build > registry-candidate.json
    python -m registry plan > provision-candidate.json
    python -m registry validate registry-candidate.json
    python -m registry validate provision-candidate.json

Use a UTF-8 shell redirect (PowerShell 7 or cmd.exe; Windows PowerShell 5.1 redirects as UTF-16, so use a suitable UTF-8 output method). Keep generated artifacts outside Git (for example an untracked/ignored path inside the repository). `validate` accepts only a repository-relative path; absolute paths, `..`, symlinks, junctions/reparse points and paths outside the repository are rejected. The JSON schemas specify document envelopes; the CLI verifies full exact content against the pinned source pack, including every nested field and hash. The compiler generates versioned specification manifests and per-agent locks on demand, not executable SKILL.md files. SPEC.md hash is distinct from a future qualified artifact hash. Third-party candidates are quarantined, not downloaded.

Dry-run intentions are not native Paperclip API payloads. No API, network, model calls, credential grants or writes are implemented. Reconcile the paused default Zeus before any future real provisioner can create the CEO; all 105 planned identities remain disabled and unqualified. Production adapter/model selection, skill artifacts, grants, live inventory, C12, authenticated recovery and approvals are subsequent gates.
