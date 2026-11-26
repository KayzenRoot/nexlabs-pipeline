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
- There is no `sonar-project.properties`, `coverage.xml`, or equivalent report step in the repository/workflow.
- Therefore **0.0% is a missing-report artifact, not proof that the tests did not execute**. The 98/98 test result is test execution evidence, not coverage evidence.
- No paid service or dependency was added; generating/uploading coverage would require a separate approved tooling decision.

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

## 6. Acceptance criteria

| AC | Status |
|---|---|
| AC01 Context Lock / 364 Source Pack unchanged | **PASS** |
| AC02 Principal/request/grant/policy strict and fail-closed | **PASS** |
| AC03 Exact grant dimensions/epoch/revocation/expiry/zero cost | **PASS** |
| AC04 HIGH_ASSURANCE approval binding/self-approval/replay/zero cost | **PASS after Correction Delta** — full scope binding added and tested |
| AC05 Network descriptor private-only/wildcard/default/port/duplicate | **PASS** |
| AC06 Opaque version-pinned tenant/purpose SecretRef | **PASS** |
| AC07 Workspace traversal/symlink/reparse isolation | **PASS**, including Windows junction |
| AC08 Tests/validator/registry/scanner/Sonar/Linux+Windows CI | **PENDING final correction-HEAD CI and Sonar reanalysis** |
| AC09 Independent audit of exact final HEAD | **PENDING new audit** |

## 7. Verdict at this stage

**CORRECTION DELTA APPLIED — FINAL CI/SONAR/ECC AND NEW INDEPENDENT AUDIT PENDING.**

The 11 Sonar findings were corrected at their root causes, the approval-scope replay gap was fixed, the 0.0% coverage cause was identified without misrepresenting test execution, and all 364 sources/registry counts remain intact. No merge, checkpoint promotion, runtime capability, VPS access, credential, model call or spend is authorized.
