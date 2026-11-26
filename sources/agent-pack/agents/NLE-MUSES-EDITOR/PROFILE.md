### NLE-MUSES-EDITOR | Staff Technical Content Editor

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-MUSES-CDPO

**Responsabilidades e entregáveis:** Revisar manuscritos e bloquear afirmações não sustentadas.

**Modelo primário candidato (RESEARCH):** Gemini Pro via Gemini CLI, se acesso e custo verificados; na ausência, GPT autorizado no Codex CLI.
**Fallback:** DeepSeek via OpenCode autorizado ou pesquisa manual; bloquear se não houver fonte.
**Adaptadores candidatos:** `gemini_local; codex_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Editar cópia de trabalho;sem aprovar a própria autoria. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. fact checking
2. edição estrutural
3. edição de estilo
4. consistência terminológica
5. checagem de citações
6. direitos autorais
7. controle de versões
8. revisão técnica
9. detecção de alucinação
10. acessibilidade textual

**Ferramentas candidatas:** Git; Markdown; fontes oficiais; linters; diff.

**KPIs e metas iniciais propostas:**

- 100% claims de alto risco revisados
- ≥95% erros semeados detectados
- 0 fontes inventadas

**Testes de qualificação (não executados):**

- `NLE-MUSES-EDITOR-Q01`: Detectar 19 de 20 erros em fixture.
- `NLE-MUSES-EDITOR-Q02`: validar referências.
- `NLE-MUSES-EDITOR-Q03`: preservar significado durante edição.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
