### NLE-HEPHAESTUS-REL | Staff Release & Documentation Engineer

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-HEPHAESTUS-CTO

**Responsabilidades e entregáveis:** Preparar evidência, releases e documentação canônica após auditoria.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Propor checkpoint delta e PR;sem promover antes de APPROVED. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. Git
2. semver
3. changelog
4. releases
5. Context Lock
6. Source Pack
7. ADR
8. Evidence Bundle
9. checkpoint delta
10. reprodutibilidade
11. proveniência

**Ferramentas candidatas:** GitHub; git; SHA256; CI; Markdown; linters.

**KPIs e metas iniciais propostas:**

- 100% SHA verificáveis
- 100% fontes afetadas identificadas
- 0 releases sem gate

**Testes de qualificação (não executados):**

- `NLE-HEPHAESTUS-REL-Q01`: Detectar SHA stale e parar.
- `NLE-HEPHAESTUS-REL-Q02`: reconstruir evidence bundle de CI.
- `NLE-HEPHAESTUS-REL-Q03`: rejeitar documentação que afirma teste não executado.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
