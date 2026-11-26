# NLE-INFRA-WO-001/CD-03 — correction candidate

Source Check: PR #3 OPEN/draft; base 8321110a2ff29aec90ffc1c384ea21f722de0497; prior HEAD feafa8c0f807c28beae1aed1424f79c941fee874; CI 45875741872 SUCCESS; no open review threads. CD-02 executor evidence reported local health, loopback, backup and isolated restore before owner claim. Owner confirms claim and subscription auth completed; independent post-claim host read-back is pending.

HIGH: Restore-Paperclip previously accepted arbitrary target and Force. Candidate fix restricts restore to a new direct-child restore-test directory, rejects existing targets/Force/reparse ancestors, and adds Windows behavioral and Python static regression tests. Tests for this candidate not yet run. Do not treat static assertions as runtime proof.

Other review items: verify full backup includes hidden files and authenticates consistent database state; backups now may include account/session secrets, keep private, never start a restored authenticated instance with external capabilities. Verify startup/health is actually the expected project container, not an unrelated HTTP 200. Resolve actual SonarCloud issues individually; public API retrieval unsuccessful, no severity inferred from quality gate. ECC action_required requests security evidence, not proof of vulnerability. See PR comment 7200438917; add focused regression evidence and rerun check if available without escalating permissions.

Context Lock CD-02 preinstall fields and old tests are retained as historical only; current runtime fields are attributed to executor/owner reports. SHA-256 fingerprints must be recomputed against corrected final candidate and verified before audit. Do not expose raw host/credential data. Confirm Docker Desktop free eligibility and no paid API/runner.

Verdict: CORRECTION REQUIRED / RUNTIME AUDIT PENDING. No merge, checkpoint promotion, agent activation, VPS access, paid services or next WO. User authorization for merge is conditional on APPROVED and read-back.
