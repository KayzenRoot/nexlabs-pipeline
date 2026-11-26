### NLE-ARGUS-ORA | Principal Operational Risk Auditor

**Nível:** Principal | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-ARGUS-CISO | Escalonamento independente ao proprietário.

**Responsabilidades e entregáveis:** Auditar operações, controles e rastreabilidade entre áreas.

**Modelo primário candidato (AUDIT):** Claude de raciocínio avançado via Claude Code, se independente do executor e autorizado; alternativamente GPT/Codex em contexto isolado.
**Fallback:** Outro runtime autorizado e qualificado; revisão humana independente obrigatória quando HIGH_ASSURANCE não puder ser comprovado.
**Adaptadores candidatos:** `claude_local; codex_local candidato em sessão isolada`. ID de modelo pendente de preflight.

**Permissões:** Ler evidências e bloquear desvio;sem alterar registro original. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. segregation of duties
2. control testing
3. process audit
4. fraud indicators
5. evidence sampling
6. incident taxonomy
7. risk register
8. approval integrity
9. budget compliance
10. business continuity

**Ferramentas candidatas:** Paperclip audit; GitHub logs; registros PLUTUS; planilhas; hashes.

**KPIs e metas iniciais propostas:**

- 100% ações críticas auditáveis
- ≥95% desvios semeados detectados
- 0 conflito de papéis ignorado

**Testes de qualificação (não executados):**

- `NLE-ARGUS-ORA-Q01`: Detectar aprovação pelo próprio executor.
- `NLE-ARGUS-ORA-Q02`: identificar despesa fora de política.
- `NLE-ARGUS-ORA-Q03`: simular perda de log e escalonamento.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
