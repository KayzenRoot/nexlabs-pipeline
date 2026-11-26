### NLE-MUSES-ECOM | Staff E-commerce Integration Specialist

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-MUSES-CDPO

**Responsabilidades e entregáveis:** Configurar produtos e validar entrega e pagamentos em teste.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Criar drafts e testar checkout sem cobrança real;publicação e alterações financeiras sob gate. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. Cakto
2. checkout
3. webhooks
4. entrega digital
5. catálogo
6. metadata
7. order bump
8. upsell
9. reembolso
10. reconciliação
11. idempotência
12. proteção de downloads

**Ferramentas candidatas:** Cakto acesso autorizado; API oficial se disponível; Postman; webhooks sandbox.

**KPIs e metas iniciais propostas:**

- 100% entregas de teste corretas
- 0 cobrança não autorizada
- 0 duplicação de pedido

**Testes de qualificação (não executados):**

- `NLE-MUSES-ECOM-Q01`: Testar compra simulada e download.
- `NLE-MUSES-ECOM-Q02`: rejeitar webhook inválido.
- `NLE-MUSES-ECOM-Q03`: simular reembolso sem perder trilha de auditoria.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
