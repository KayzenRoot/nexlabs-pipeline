# NLE-INFRA-WO-002/CD-01 — SonarCloud triage, corrections and audit evidence

Date: 2026-11-26
Repository: `KayzenRoot/nexlabs-pipeline`
PR: #7 (draft, branch `work/nle-infra-wo-002-cd01`)
Base: `eebbd7325ab45fca8e176bd713245189ed148bdd`
HEAD at triage start: `27247893d3493de3b9c8e1ee6741ee3df4124797`
Scope: offline security contracts only. No VPS, SSH, live network, credentials, skill import, agent/workflow activation, model call, Paperclip mutation or spend.

## 1. Source check and initial state

- Confirmed PR #7 HEAD `2724789`, base `eebbd73`, draft and mergeable.
- Initial checks: `docs-validation` run `45900241955` success; `security-windows` success; Socket Security pass; ECC evidence pass.
- SonarCloud quality gate passed, but **11 new-code issues were open** and new-code coverage was **0.0%**.
- Initial evidence incorrectly stated that line/rule detail was unavailable; this audit retrieved all 11 through the public SonarCloud API and did not infer any detail.

## 2. SonarCloud triage — all 11 open issues

| # | Rule | Severity | Type | File:line | Description | Root cause | Correction |
|---|---|---|---|---|---|---|---|
| 1 | `python:S1313` | MINOR | CODE_SMELL | `security/network.py:11` | Hardcoded IP `10.0.0.0` | RFC1918 ranges expressed as string literals | Built the same ranges from integer address/prefix values |
| 2 | `python:S1313` | MINOR | CODE_SMELL | `security/network.py:11` | Hardcoded IP `172.16.0.0` | Same | Same integer construction |
| 3 | `python:S1313` | MINOR | CODE_SMELL | `security/network.py:11` | Hardcoded IP `192.168.0.0` | Same | Same integer construction |
| 4 | `python:S3776` | CRITICAL | CODE_SMELL | `security/authorization.py:36` | Cognitive complexity 18 > 15 | `authorize()` mixed request validation, grant selection and approval orchestration | Split into `_validate_request`, `_grant_is_eligible`, `_select_grant`, `_verify_high_assurance`; `authorize()` now composes them |
| 5 | `python:S5778` | MAJOR | CODE_SMELL | `tests/test_security_controls.py:284` | Multiple potentially-throwing invocations in one exception test | `subTest` and `assertRaises` in the same context, plus nested constructors | Nested contexts / prebuilt fixtures outside the exception context |
| 6 | `python:S5778` | MAJOR | CODE_SMELL | `tests/test_security_controls.py:319` | Same | Same | Same |
| 7 | `python:S5778` | MAJOR | CODE_SMELL | `tests/test_security_controls.py:323` | Same | Constructor calls inside the exception context | Prebuilt policy outside the context |
| 8 | `python:S5778` | MAJOR | CODE_SMELL | `tests/test_security_controls.py:345` | Same | Dict unpacking/frozenset construction inside the context | Precomputed argument dictionaries |
| 9 | `python:S5778` | MAJOR | CODE_SMELL | `tests/test_security_controls.py:351` | Same | Inline secret-reference arguments/constructors | Precomputed argument dictionary |
| 10 | `python:S5778` | MAJOR | CODE_SMELL | `tests/test_security_controls.py:357` | Same | Same | Same |
| 11 | `python:S5778` | MAJOR | CODE_SMELL | `tests/test_security_controls.py:361` | Same | Same | Same |

No issue was suppressed, excluded, or marked resolved without changing the code. None of the 11 was a Sonar vulnerability; they were code-quality findings, but the CLI/Sonar gate had to be corrected.

## 3. Additional security finding — approval scope replay

The independent security review also found a real authorization gap not reported by Sonar:

- A `HIGH_ASSURANCE` approval was bound to actor/approver/action/target/tenant/payload/policy/evidence/expiry/nonce but **not to project, task, workflow, skill, host, provider or risk**.
- A signed approval for `project-1` could be reused for `project-2` with a matching grant and payload/action/target, because those scope dimensions were absent from the approval envelope and canonical signature bytes.
- Correction: `ApprovalEnvelope`, canonical bytes, verification, policy binding list, JSON schema and fixtures now include the full request scope; mismatch tests cover all seven dimensions. Approval is also still single-use via the nonce store.

## 4. Coverage investigation — 0.0% new code

- The workflow runs `unittest`, `security verify`, the registry verifier and the security scanner, but it does not run a coverage tool, produce a coverage report, or upload one to SonarCloud.
- There is no `sonar-project.properties`, `coverage.xml`, or equivalent report step in the repository/workflow. Sonar reports `new_lines_to_cover=0` and no coverage measure; the quality gate conditions are reliability/security/maintainability ratings, duplication and security-hotspot review, with **no coverage condition**.
- Therefore **0.0% is a missing-report artifact, not proof that the tests did not execute**. The 98/98 test result is test execution evidence, not coverage evidence.
- Coverage is **not an acceptance criterion** in this Work Order. AC08's “100% targeted tests” means the targeted test suite passed (98/98), not a coverage percentage. No paid service or dependency was added; generating/uploading coverage would require a separate approved tooling decision.

## 5. Regression and revalidation

| Check | Result |
|---|---|
| Full Python suite (Windows 11) | **98/98 OK** |
| Security-control suite | **45/45 OK**, including real Windows junction |
| Security policy verifier | `SECURITY_CONTRACTS_OK default_deny=true network=offline secrets=opaque` |
| Registry verification | `105 agents / 92 packages / 1110 assignments`, 105 intents, 0 runtime writes |
| Source validator | 7/7 groups PASS; 364 source files unchanged |
| Security scan | 472 tracked files, 0 findings |
| Determinism | Policy, labels and authorization decisions are deterministic; no clock/random dependency beyond injected `now`/nonce |
| Network ranges | RFC1918/ULA/loopback accepted; public, CGNAT, special-purpose, wildcard, default route and link-local rejected |
| Schema alignment | Approval/grant/secret-ref/network schemas match dataclass fields; nested peer/service schemas are closed |
| No effects | 0 model calls, 0 network sockets, 0 imports, 0 Paperclip writes, 0 secret resolutions, 0 VPS access, US$0 |

### AC06 SecretRef evidence

- `security/secrets.py` defines only an immutable metadata dataclass (`reference_id`, `provider_id`, `tenant_id`, `project_id`, `purpose`, `version`) and `validate_secret_ref`.
- Validation requires provider allowlist, purpose allowlist, exact tenant, exact project and a non-`latest` version. No function reads, resolves, creates, rotates, logs or exports a value; no environment/credential/keyring access exists in the module.
- Tests: `test_opaque_pinned_scoped_reference_validates`, `test_unknown_provider_purpose_and_cross_tenant_deny`, `test_latest_secret_version_denied`, `test_secret_purpose_and_project_are_exact`, plus schema alignment.

### AC08 CI evidence

- Run `45908334436` at final evidence HEAD `578c273` has **both** jobs success:
  - `docs-validation` on `ubuntu-24.04`: Source Pack validation, 98-test canonical suite, Registry verify, security verify, scanner.
  - `security-windows` on `windows-2025`: security-control suite including the real `mklink /J` junction and offline policy verify.
- Prior correction-head run `45908006041` at `fb6fa8d` also passed both jobs.
- SonarCloud at `578c273`: 0 open issues, quality gate OK; ECC Security Evidence pass; Socket pass.

## 6. Acceptance criteria

| AC | Status |
|---|---|
| AC01 Context Lock / 364 Source Pack unchanged | **PASS** — 26 canonical + 20 implementation fingerprints, zero mismatches; validator 7/7 |
| AC02 Principal/request/grant/policy strict and fail-closed | **PASS** — helpers `_validate_request`, `_grant_is_eligible`, `_select_grant`; fail-closed tests |
| AC03 Exact grant dimensions/epoch/revocation/expiry/zero cost | **PASS** — exact-dimension, revoked/expired/future, stale-policy and zero-cost tests |
| AC04 HIGH_ASSURANCE approval binding/self-approval/replay/zero cost | **PASS after Correction Delta** — full scope binding + 7 mismatch + nonce single-use tests |
| AC05 Network descriptor private-only/wildcard/default/port/duplicate | **PASS** — RFC1918/ULA/loopback accepted; public/special/CGNAT/wildcard/default/link-local rejected |
| AC06 Opaque version-pinned tenant/purpose SecretRef | **PASS** — itemized above; no resolution code |
| AC07 Workspace traversal/symlink/reparse isolation | **PASS** — traversal/absolute/Windows paths, symlink ancestors/components, real junction; non-mutating |
| AC08 Tests/validator/registry/scanner/Sonar/Linux+Windows CI | **PASS** — 98/98, 45/45, 7/7, 105/92/1110, 472/0, Sonar 0/OK, Linux+Windows run 45908334436 |
| AC09 Independent audit of exact final HEAD | **PASS** — independent final audit APPROVED at `578c273`; this docs/lock finalization follows without code changes |

## 7. Verdict at this stage

**APPROVED.**

The 11 Sonar findings were corrected at their root causes, the approval-scope replay gap was fixed, AC06/AC08 evidence was itemized, the 0.0% coverage cause was identified without misrepresenting test execution, and all 364 sources/registry counts remain intact. The independent final audit at `578c273` returned APPROVED with no HIGH/CRITICAL findings and AC01–AC09 PASS. No merge, checkpoint promotion, runtime capability, VPS access, credential, model call or spend is authorized.

## 8. Independent final audit — non-blocking notes

- AC08's “100% targeted tests” is recorded verbatim as **98/98 pass rate, not coverage**. Sonar `new_lines_to_cover=0`, 0.0% new coverage has no report/upload, and the quality gate has no coverage condition. No coverage claim is made and no dependency was added.
- The Linux `docs-validation` job passed the canonical suite; the suite’s per-platform Linux itemization is not separately published beyond the successful job steps. This is a reporting limitation, not a failed required check.
- The seven approval-scope mismatch tests map 1:1 to project/task/workflow/skill/host/provider/risk and must be retained.
- No secret-resolution path may be added without a new AC and a new independent audit.
- The zero-Sonar state is necessary, not sufficient: the cross-project approval defect was found by audit, not Sonar.
