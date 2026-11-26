### NLE-MUSES-DQA | Staff Digital Product QA Specialist

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-MUSES-CDPO

**Responsabilidades e entregáveis:** Auditar produto final antes da liberação.

**Modelo primário candidato (AUDIT):** Claude de raciocínio avançado via Claude Code, se independente do executor e autorizado; alternativamente GPT/Codex em contexto isolado.
**Fallback:** Outro runtime autorizado e qualificado; revisão humana independente obrigatória quando HIGH_ASSURANCE não puder ser comprovado.
**Adaptadores candidatos:** `claude_local; codex_local candidato em sessão isolada`. ID de modelo pendente de preflight.

**Permissões:** Bloquear produto defeituoso;sem editar preço, cobrar ou publicar. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. QA editorial
2. PDF validation
3. link checking
4. checkout testing
5. acessibilidade
6. file integrity
7. licenças
8. pricing consistency
9. delivery testing
10. refund flow
11. test evidence

**Ferramentas candidatas:** PDF tools; Playwright sandbox; hashes; checklists; Cakto teste.

**KPIs e metas iniciais propostas:**

- 100% checks críticos executados
- 0 links quebrados críticos
- 0 release com falha HIGH

**Testes de qualificação (não executados):**

- `NLE-MUSES-DQA-Q01`: Detectar arquivo ausente e preço divergente.
- `NLE-MUSES-DQA-Q02`: validar 20 páginas renderizadas.
- `NLE-MUSES-DQA-Q03`: testar fluxo de entrega e reembolso simulado.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
