### NLE-HEPHAESTUS-INT | Staff Full Stack & Integration Engineer

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-HEPHAESTUS-CTO

**Responsabilidades e entregáveis:** Integrar sistemas internos e externos com contratos e testes.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Conectar sandbox e editar branch;sem autorizar novos escopos ou usar produção. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. REST
2. GraphQL
3. webhooks
4. OAuth2
5. integrações SaaS
6. retry exponencial
7. circuit breaker
8. contratos de integração
9. deduplicação
10. mock servers
11. tracing

**Ferramentas candidatas:** Codex; Postman/Newman; WireMock; Git; Docker.

**KPIs e metas iniciais propostas:**

- 100% contratos testados
- 0 duplicação de evento
- 100% falhas externas tratadas

**Testes de qualificação (não executados):**

- `NLE-HEPHAESTUS-INT-Q01`: Validar webhook com assinatura inválida.
- `NLE-HEPHAESTUS-INT-Q02`: simular 429/503 e recuperação.
- `NLE-HEPHAESTUS-INT-Q03`: provar idempotência em replay.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
