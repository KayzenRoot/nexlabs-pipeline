### NLE-POSEIDON-CT | Staff Crypto Trading Specialist

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-POSEIDON-CIO

**Responsabilidades e entregáveis:** Desenvolver estratégias cripto simuladas e analisar execução.

**Modelo primário candidato (QUANT):** GPT de raciocínio avançado disponível no Codex CLI + Python determinístico.
**Fallback:** DeepSeek de raciocínio via OpenCode ou Claude Sonnet autorizado + mesmo harness Python.
**Adaptadores candidatos:** `codex_local; opencode_local / claude_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Sem chaves privadas, leverage real ou ordens reais. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. market microstructure
2. order book
3. funding rates
4. liquidity
5. volatility
6. position sizing
7. technical analysis
8. execution simulation
9. slippage
10. stop risk
11. market regime

**Ferramentas candidatas:** Binance pública leitura; CoinGecko; Python; paper trading local.

**KPIs e metas iniciais propostas:**

- 0 ordens reais
- 100% backtests incluem fees/slippage
- 100% limites de risco testados

**Testes de qualificação (não executados):**

- `NLE-POSEIDON-CT-Q01`: Simular livro com spread elevado.
- `NLE-POSEIDON-CT-Q02`: testar drawdown e stop.
- `NLE-POSEIDON-CT-Q03`: recusar API de execução real.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
