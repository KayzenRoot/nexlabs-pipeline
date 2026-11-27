# Unified Backlog

## Current execution state | 2026-11-27
- NLE-BOOTSTRAP-001 is APPROVED and squash-merged; PR #1 and PR #2 are closed/merged.
- NLE-INFRA-WO-001 APPROVED and squash-merged at 28a40b0f6ddf3b4dee5f2663ec96639a74cc49fd; checkpoint promoted.
- NLE-SR-WO-001/CD-01 APPROVED and squash-merged in PR #5 at 126de4d059915abf55eb03fa51e53c0bc8ab0cd9; checkpoint promoted. Registry is offline/dry-run only; 53/53 tests, CI, SonarCloud, Socket and ECC passed.
- NLE-INFRA-WO-002/CD-01 APPROVED and squash-merged in PR #7 at `6d6f87c60144386c1242673322d147338a4dab61`; checkpoint promoted via PR #8 at `6eacae4c8b6f4d3a5c43c84074b2061e6dca49db`. Offline security contracts only; 98/98 tests, 45/45 security controls, CI Linux/Windows, SonarCloud 0/gate OK, Socket and ECC passed. No runtime, network, credentials or spend.
- Local-first deliverables: portable compose, pinned official image digest with linux/amd64 and linux/arm64 manifests, localhost-only access on `127.0.0.1:3100`, protected local secrets outside Git, embedded PostgreSQL persistence, healthcheck, PowerShell start/stop/status/backup/restore scripts, VPS-oriented external PostgreSQL preparation and operational docs.
- No VPS SSH/deploy, agent import/hiring, skill activation, workflow activation, heartbeat, external effect, API key or spend is authorized by NLE-INFRA-WO-001/CD-03. Docker Desktop 4.100.1 and the Paperclip container are running healthy locally; persistence, restart, backup and isolated restore were validated. The owner claim is verified (`bootstrapStatus=ready`) and Codex subscription auth is **PASS** via the official Paperclip-managed connection (`tool_connections` active, `credential_source=paperclip_vault`, active grant; live usage check succeeded), so **AC16 is MET**. One paused default agent (`Zeus`) exists from the claim and has no task execution. CD-03 is **APPROVED**; auth-gate CI run `45892550947` and independent read-only audit passed. No agent may run without separate authorization.
- After NLE-INFRA-WO-002 checkpoint integration/read-back, continue with NLE-WF-WO-001, then NLE-INFRA-WO-003. Do not parallelize or skip dependencies.

NLE-WF-WO-001 is next after NLE-INFRA-WO-002 checkpoint integration/read-back; HIGH_ASSURANCE event/authorization/ledger contract, no activation. Activate no subsequent WO until approved. Sequence below preserves all 40 prior IDs (5 families x 8). INFRA/CC short forms in original docs correspond to NLE-INFRA/NLE-CC. Each row is an umbrella if too large: executor proposes small slices with stable child ID, acceptance and evidence; no parallel activation before gates. No duplicate auth/queue/FinOps/evaluation: first implementation owner establishes contract, later WOs extend or qualify existing components. Preflight may reveal prerequisite not met (e.g., GOV/SEC/FIN pilot skills, Web3 skill qualification before ENG production, embedding resources before ingestion); stop and propose dependency-only reordering for audit, never silently skip gate. SR-WO-003..007 precedem o piloto WF-WO-002; qualificar somente os agentes necessários em cada WO de skills, e todos no SR-WO-008. WF-WO-001 resolve C12 com contrato dispatch-only e testes sem conceder acesso. Web3 permanece local/simulado. No real production operations authorized by a backlog row. Audit dependencies before compiling each WO.

| Ordem | ID | Escopo | Risco |
|---:|---|---|---|
| 1 | NLE-INFRA-WO-001 | Inventário e compatibilidade read-only | LOW |
| 2 | NLE-SR-WO-001 | Registry schema, locks, quarentena e validador | ELEVATED |
| 3 | NLE-INFRA-WO-002 | Rede privada, identidade, secrets e isolamento | HIGH_ASSURANCE |
| 4 | NLE-WF-WO-001 | Contrato de eventos, autorização e ledger | HIGH_ASSURANCE |
| 5 | NLE-INFRA-WO-003 | Paperclip e PostgreSQL privado, backups iniciais | HIGH_ASSURANCE |
| 6 | NLE-INFRA-WO-004 | Codex oficial, worker Windows, cancelamento | HIGH_ASSURANCE |
| 7 | NLE-INFRA-WO-005 | Fila/quotas/FinOps, 9Router opcional | HIGH_ASSURANCE |
| 8 | NLE-SR-WO-002 | 12 core packages, harness e tool gateway | HIGH_ASSURANCE |
| 9 | NLE-INT-WO-001 | Foundation schemas, ACL, adapters e fixtures | HIGH_ASSURANCE |
| 10 | NLE-INFRA-WO-006 | Recursos do Intelligence Hub e Registry | ELEVATED |
| 11 | NLE-INT-WO-002 | Ingestão, proveniência, retenção e embeddings | HIGH_ASSURANCE |
| 12 | NLE-INT-WO-003 | RAG híbrido e Context Pack | HIGH_ASSURANCE |
| 13 | NLE-INT-WO-004 | Grafo temporal e ACL de caminhos | HIGH_ASSURANCE |
| 14 | NLE-INT-WO-005 | Memória, feedback, evolução de skills | HIGH_ASSURANCE |
| 15 | NLE-INT-WO-006 | Evaluation/FinOps e benchmarks | ELEVATED |
| 16 | NLE-CC-WO-001 | Preflight SDK, plugin vs sidecar, design system | ELEVATED |
| 17 | NLE-SR-WO-003 | Skills engenharia/governança piloto | ELEVATED |
| 18 | NLE-SR-WO-004 | Skills comerciais/marketing piloto | ELEVATED |
| 19 | NLE-SR-WO-005 | Skills digitais e checkout mock | ELEVATED |
| 20 | NLE-SR-WO-006 | Demais competências corporativas, pesquisa e segurança | ELEVATED |
| 21 | NLE-SR-WO-007 | Skills Web3 e finanças em laboratório | HIGH_ASSURANCE |
| 22 | NLE-WF-WO-002 | Dispatcher Paperclip, GOV/SEC/FIN piloto | HIGH_ASSURANCE |
| 23 | NLE-CC-WO-002 | Shell, dashboard, ZEUS, integração nativa | ELEVATED |
| 24 | NLE-WF-WO-003 | Software Factory e GitHub teste | ELEVATED |
| 25 | NLE-WF-WO-004 | Pesquisa, B2B, CRM e orgânico mock | ELEVATED |
| 26 | NLE-CC-WO-003 | CRM/vendas/clientes e Software Factory | ELEVATED |
| 27 | NLE-WF-WO-005 | E-books, checkout, entrega e conciliação | HIGH_ASSURANCE |
| 28 | NLE-WF-WO-006 | Paid media read-only e dry-run | HIGH_ASSURANCE |
| 29 | NLE-CC-WO-004 | Marketing, ads, social, e-books | ELEVATED |
| 30 | NLE-WF-WO-007 | Finanças corporativas e paper trading | HIGH_ASSURANCE |
| 31 | NLE-CC-WO-005 | Finanças/FinOps/trading simulado | HIGH_ASSURANCE |
| 32 | NLE-INT-WO-007 | Integração bindings completos 105/92/62 | HIGH_ASSURANCE |
| 33 | NLE-CC-WO-006 | Intelligence Center, skills e benchmarks | HIGH_ASSURANCE |
| 34 | NLE-INFRA-WO-007 | Monitoramento, restore, recuperação | HIGH_ASSURANCE |
| 35 | NLE-CC-WO-007 | Infra, security, approvals e mobile | HIGH_ASSURANCE |
| 36 | NLE-SR-WO-008 | Qualificação dos 105 agentes e rollback | HIGH_ASSURANCE |
| 37 | NLE-WF-WO-008 | Operações e qualificação ponta a ponta | HIGH_ASSURANCE |
| 38 | NLE-INT-WO-008 | Red team, recovery e qualificação INT | HIGH_ASSURANCE |
| 39 | NLE-INFRA-WO-008 | Qualificação infraestrutura e rollout controlado | HIGH_ASSURANCE |
| 40 | NLE-CC-WO-008 | Qualificação integrada UI e release gate | HIGH_ASSURANCE |

Final release: only after all domain gates and v1.0 DoD; production private authorization separate. IMPORTANT/FUTURE items in Scope; no automatic expansion.
