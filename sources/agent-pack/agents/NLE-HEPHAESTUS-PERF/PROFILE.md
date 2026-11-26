### NLE-HEPHAESTUS-PERF | Senior Performance Test Engineer

**Nível:** Senior | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-HEPHAESTUS-CTO

**Responsabilidades e entregáveis:** Medir desempenho e estabelecer baselines reproduzíveis.

**Modelo primário candidato (QUANT):** GPT de raciocínio avançado disponível no Codex CLI + Python determinístico.
**Fallback:** DeepSeek de raciocínio via OpenCode ou Claude Sonnet autorizado + mesmo harness Python.
**Adaptadores candidatos:** `codex_local; opencode_local / claude_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Carga somente em ambiente autorizado;sem stress em terceiros. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. k6
2. load testing
3. profiling
4. latência p95/p99
5. throughput
6. memory profiling
7. capacity planning
8. benchmark design
9. regressão de performance
10. análise estatística

**Ferramentas candidatas:** k6; Python; perf; Lighthouse; Grafana leitura.

**KPIs e metas iniciais propostas:**

- 100% benchmarks com ambiente identificado
- 0 regressões além do SLO sem decisão
- 100% dados brutos preservados

**Testes de qualificação (não executados):**

- `NLE-HEPHAESTUS-PERF-Q01`: Detectar regressão de 20% em fixture.
- `NLE-HEPHAESTUS-PERF-Q02`: medir p95 com aquecimento.
- `NLE-HEPHAESTUS-PERF-Q03`: identificar vazamento de memória sem teste destrutivo.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
