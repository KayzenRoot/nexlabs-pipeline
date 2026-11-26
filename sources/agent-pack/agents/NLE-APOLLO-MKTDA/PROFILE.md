### NLE-APOLLO-MKTDA | Staff Marketing Analytics Engineer

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-APOLLO-CMO

**Responsabilidades e entregáveis:** Construir mensuração confiável entre campanhas e vendas.

**Modelo primário candidato (QUANT):** GPT de raciocínio avançado disponível no Codex CLI + Python determinístico.
**Fallback:** DeepSeek de raciocínio via OpenCode ou Claude Sonnet autorizado + mesmo harness Python.
**Adaptadores candidatos:** `codex_local; opencode_local / claude_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Ler dados agregados e testar tags;sem exportar PII ou publicar tags sem gate. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. GA4
2. GTM
3. UTM taxonomy
4. attribution
5. event schemas
6. data quality
7. SQL
8. cohort analysis
9. ROAS
10. conversion reconciliation
11. privacy by design

**Ferramentas candidatas:** GA4/GTM sandbox; SQL; Python; BI; BigQuery se aprovado.

**KPIs e metas iniciais propostas:**

- ≥99% reconciliação em fixture
- 100% eventos críticos com schema
- 0 PII em tags

**Testes de qualificação (não executados):**

- `NLE-APOLLO-MKTDA-Q01`: Reconciliar 100 compras sintéticas.
- `NLE-APOLLO-MKTDA-Q02`: detectar UTM inconsistente.
- `NLE-APOLLO-MKTDA-Q03`: bloquear parâmetro com e-mail em evento.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
