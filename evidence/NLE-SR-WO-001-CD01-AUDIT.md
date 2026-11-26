# NLE-SR-WO-001/CD-01 — Independent audit and Correction Delta

Date: 2026-11-26
Repository: `KayzenRoot/nexlabs-pipeline`
PR: #5 (draft, branch `work/nle-sr-wo-001`)
Base: `05764c3d8e3050ddec9e4b8a010232f150704acb`
HEAD at first audit: `c5f7506304abf92508ce2c03aa96e5ebe7b1cdd3`
CI at first audit: `docs-validation` run `45894018049` success; SonarCloud check **failure**.

Scope: offline Registry compiler, schemas, policy, locks, quarantine and dry-run provision intentions. No VPS, agent activation, skill import, API key, model call, Paperclip mutation or spend.

## 1. Source check

- Fetched the existing PR branch and confirmed HEAD `c5f7506`, base `05764c3`.
- The diff is limited to the registry compiler, policy, schemas, tests, README, Context Lock and Work Order.
- No `sources/` bytes, no Paperclip/deploy/runtime files and no executable SKILL.md were changed.
- The original 364-file Source Pack remains the pinned baseline (`locks/source-lock.json` SHA-256 `a72bc69b…231e`).

## 2. Independent audit — initial result

| Check | Result |
|---|---|
| Canonical source validator | 7/7 groups PASS |
| Python suite | **50/50 OK** |
| Counts | 105 agents, 92 packages, 1,110 assignments, 1,071 competencies |
| Links / individual scenarios | 183 agent-package links / 316 qualification tests |
| Quarantine | 18 entries: 17 quarantined external sources + OWN authoring |
| Dry-run | 105 intents, first `NLE-ZEUS-CEO` with `RECONCILE_EXISTING_BEFORE_CREATE`, 0 creates/updates/model calls |
| Determinism | Build byte-identical twice; plan byte-identical twice |
| CLI on Windows 11 | `verify`, `build`, `plan`, `validate` work with PowerShell 7 |
| Context Lock | 16 Git blob fingerprints matched current files |
| SonarCloud | **FAIL**: `pythonsecurity:S8707` at `registry/core.py:57`, security rating 3 ERROR |
| ECC | Security evidence gate **pass** |
| Paperclip/model/network | No calls, imports or runtime changes found |

### Findings

1. **HIGH — path traversal / arbitrary local document read.** `registry/core.py:56-58` read any `Path` directly. `registry/__main__.py:26` passed the CLI argument `args.document` to it without containment or link validation. `python -m registry validate <outside-path>` could read a JSON file outside the repository, follow a symlink/reparse point and process it. No content was printed, but the CLI violated the deny-by-default path policy and SonarCloud correctly failed the security gate. **Correction required before APPROVED.**
2. **MEDIUM — Windows link regression gap.** The only symlink test skipped when Windows symlink creation was unavailable, so the claimed reparse-point rejection was not behaviorally exercised on the actual Windows 11 host.
3. **LOW — stale evidence/lock state.** The PR body still said “Tests and CI pending”; the Context Lock had `ci: PENDING`, no SHA-256 map and did not cover the new registry files. The README’s “keep artifacts outside Git” wording did not explain that `validate` confines reads to the repository.

## 3. Correction Delta

- `read_json(path, root)` now resolves the candidate strictly, rejects paths outside `root`, rejects symlink/reparse components through `safe_path`, and only then reads the contained regular file. Missing paths produce a controlled `RegistryError`.
- `safe_path()` now converts a missing/unreadable component into `SOURCE_NOT_REGULAR` instead of leaking `FileNotFoundError`.
- CLI `validate` applies `safe_path(ROOT, …)` before reading and accepts only repository-relative paths; absolute paths, `..`, symlinks, junctions and outside-root paths are rejected.
- Tests added: outside-root read rejection, CLI outside-path rejection, and a real Windows `mklink /J` junction rejection.
- README clarifies the repository-relative constraint and untracked/ignored artifact placement.
- Context Lock expanded to the registry/test/evidence files with both SHA-256 and Git blob identities.

## 4. Revalidation after correction

| Check | Result |
|---|---|
| Python suite | **53/53 OK** (50 original + 3 new regression tests) |
| Canonical validator | 7/7 groups PASS |
| CLI `verify` | `REGISTRY_OK agents=105 packages=92 assignments=1110 intents=105 runtime_writes=0` |
| CLI `build` → `validate` (repo-relative artifact) | `REGISTRY_DOCUMENT_OK` |
| CLI `plan` → `validate` (repo-relative artifact) | `REGISTRY_DOCUMENT_OK` |
| CLI outside-root path | `REGISTRY_REJECTED RegistryError` |
| Windows junction | `SOURCE_LINK_FORBIDDEN` |
| Determinism | Build SHA-256 `09882f26…7d91`; plan SHA-256 `9d273143…ef53`; repeat byte-identical |
| Counts | 105 / 92 / 1110 / 1071 / 183 / 316 / 17+OWN |
| Source Pack | 364/364 lock entries; no `sources/` diff |
| Security scan | 450 tracked files, 0 findings |
| Paperclip/deploy diff | none; no API/model/import calls |

## 5. Gates

- **SonarCloud:** the initial S8707 failure is addressed; final reanalysis at the correction HEAD is required to confirm 0 issues and the quality gate returning to OK.
- **ECC:** initial evidence gate passed; rerun at the correction HEAD is required.
- **CI:** initial `docs-validation` run `45894018049` passed; correction HEAD CI is required.
- **Independent audit:** first audit produced this Correction Delta; a new read-only audit of the correction HEAD is required before APPROVED.

## 6. Acceptance matrix

| AC | Status |
|---|---|
| AC01 baseline lock and original sources | **PASS** — 364/364, validator 7/7 |
| AC02 manifests, locks, assignments, competencies, links, tests | **PASS** — 92/105/1110/1071/183/316 |
| AC03 quarantine / no artifact or grant | **PASS** — 17 quarantined + OWN authoring; zero grants |
| AC04 deterministic/fail-closed/path/link/policy | **PASS after Correction Delta** — outside-root read and Windows junction rejected; 53/53 |
| AC05 105 topological paused intents, zero effects, Zeus reconciliation | **PASS** — CEO first with reconcile intent; 0 creates/updates/model calls |
| AC06 tests, validator, scanner, required CI | **PENDING final correction-HEAD CI** |
| AC07 independent review of exact head and evidence | **PENDING new independent audit** |

## 7. Verdict

**CORRECTION DELTA APPLIED — PENDING FINAL CI AND NEW INDEPENDENT AUDIT.**

The initial HIGH security finding (path traversal in the validate CLI), the Windows junction coverage gap and the stale evidence/lock state were corrected. The 50 original tests remain passing; three regressions were added (53/53). The work is not APPROVED until the correction HEAD passes CI/SonarCloud/ECC and a new independent read-only audit confirms it. No merge, checkpoint promotion, agent/skill activation, Paperclip change, VPS access or spend is authorized.
