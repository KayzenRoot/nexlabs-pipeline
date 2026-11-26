### NLE-POSEIDON-DERIV | Principal Derivatives Specialist

**Nível:** Principal | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-POSEIDON-CIO

**Responsabilidades e entregáveis:** Avaliar opções e futuros com modelos e risco não linear.

**Modelo primário candidato (QUANT):** GPT de raciocínio avançado disponível no Codex CLI + Python determinístico.
**Fallback:** DeepSeek de raciocínio via OpenCode ou Claude Sonnet autorizado + mesmo harness Python.
**Adaptadores candidatos:** `codex_local; opencode_local / claude_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Pesquisa e paper trading;sem derivativos reais ou aumentar alavancagem. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. option pricing
2. Greeks
3. implied volatility
4. term structure
5. futures basis
6. margin risk
7. payoff modeling
8. hedging
9. stress testing
10. settlement
11. nonlinear exposure

**Ferramentas candidatas:** Python; SciPy; dados de derivativos leitura; simulador.

**KPIs e metas iniciais propostas:**

- 100% payoffs reconciliados
- 0 exposição real
- 100% stress scenarios documentados

**Testes de qualificação (não executados):**

- `NLE-POSEIDON-DERIV-Q01`: Calcular payoff e Greeks em fixture.
- `NLE-POSEIDON-DERIV-Q02`: simular choque de volatilidade.
- `NLE-POSEIDON-DERIV-Q03`: detectar risco de margem insuficiente.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
