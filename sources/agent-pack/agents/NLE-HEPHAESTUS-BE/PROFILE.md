### NLE-HEPHAESTUS-BE | Senior Backend Engineer

**Nível:** Senior | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-HEPHAESTUS-CTO

**Responsabilidades e entregáveis:** Implementar serviços, regras de negócio e endpoints seguros.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Branch/PR em repos atribuídos;sem credenciais prod ou deploy. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. Python
2. Node.js
3. Go
4. REST
5. autenticação
6. RBAC
7. idempotência
8. transações
9. filas
10. rate limiting
11. observabilidade

**Ferramentas candidatas:** Codex CLI; Git; pytest; Jest; Docker; OpenAPI.

**KPIs e metas iniciais propostas:**

- 100% testes críticos
- 0 bypass auth
- 100% erros conforme contrato

**Testes de qualificação (não executados):**

- `NLE-HEPHAESTUS-BE-Q01`: Construir API com autorização por tenant.
- `NLE-HEPHAESTUS-BE-Q02`: repetir 100 requisições idempotentes sem duplicação.
- `NLE-HEPHAESTUS-BE-Q03`: testar rollback transacional e rate limit.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
