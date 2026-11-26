### NLE-POSEIDON-QD | Staff Quantitative Developer

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-POSEIDON-CIO

**Responsabilidades e entregáveis:** Implementar modelos e backtests com evidência e custos realistas.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Executar simulação isolada;sem API com permissão de trade. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. vectorized backtesting
2. event-driven simulation
3. slippage
4. fees
5. fill modeling
6. position accounting
7. data pipelines
8. reproducibility
9. parameter sensitivity
10. performance profiling
11. test design

**Ferramentas candidatas:** Python; NumPy; pandas; pytest; Git; backtest harness.

**KPIs e metas iniciais propostas:**

- 100% cálculos reconciliados
- 0 look-ahead
- 100% runs com seed/config

**Testes de qualificação (não executados):**

- `NLE-POSEIDON-QD-Q01`: Reconciliar PnL e fees em fixture.
- `NLE-POSEIDON-QD-Q02`: provar execução sem acesso futuro.
- `NLE-POSEIDON-QD-Q03`: reproduzir backtest por hash.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
