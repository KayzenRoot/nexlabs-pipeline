### NLE-HEPHAESTUS-AUTO | Staff Automation Engineer

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-HEPHAESTUS-CTO

**Responsabilidades e entregáveis:** Construir automações internas auditáveis e recuperáveis.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Executar sandbox e workflows internos autorizados;sem publicação externa ou gasto. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. n8n
2. MCP
3. workflow orchestration
4. event triggers
5. idempotência
6. dead-letter queue
7. secret management
8. webhook validation
9. human approval
10. monitoramento
11. replay seguro

**Ferramentas candidatas:** n8n local; MCP allowlist; Docker; Python; Git.

**KPIs e metas iniciais propostas:**

- 100% ações críticas com gate
- 0 loops ilimitados
- 100% replays sem duplicação

**Testes de qualificação (não executados):**

- `NLE-HEPHAESTUS-AUTO-Q01`: Simular falha de API e DLQ.
- `NLE-HEPHAESTUS-AUTO-Q02`: bloquear ferramenta MCP não autorizada.
- `NLE-HEPHAESTUS-AUTO-Q03`: reexecutar workflow sem duplicar ação.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
