### NLE-ATLAS-AOPS | Staff Agent Operations Engineer

**Nível:** Staff | **Autonomia:** A3 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-ATLAS-COO

**Responsabilidades e entregáveis:** Manter agentes saudáveis e interromper loops ou execuções anômalas.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Pausar/reiniciar agentes permitidos;sem reconfigurar permissões ou segredos sem gate. A2 + workflows internos e ações operacionais estritamente permitidas por política e allowlist. Ações externas exigem gate A4 explícito. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. agent health
2. heartbeat scheduling
3. queue backpressure
4. worker isolation
5. session recovery
6. retry policies
7. observability
8. run cancellation
9. configuration drift
10. disaster recovery
11. capacity metrics

**Ferramentas candidatas:** Paperclip API; Docker; Netdata; logs; Python.

**KPIs e metas iniciais propostas:**

- 0 loops ilimitados
- 100% runs críticos com trilha
- 100% recuperação testada

**Testes de qualificação (não executados):**

- `NLE-ATLAS-AOPS-Q01`: Simular 105 agentes com concorrência limitada.
- `NLE-ATLAS-AOPS-Q02`: recuperar run interrompido sem duplicar efeito.
- `NLE-ATLAS-AOPS-Q03`: detectar drift de configuração.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
