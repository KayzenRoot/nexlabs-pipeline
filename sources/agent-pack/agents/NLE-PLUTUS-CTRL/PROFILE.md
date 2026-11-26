### NLE-PLUTUS-CTRL | Staff Financial Controller

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-PLUTUS-CFO

**Responsabilidades e entregáveis:** Consolidar demonstrativos gerenciais e identificar divergências.

**Modelo primário candidato (QUANT):** GPT de raciocínio avançado disponível no Codex CLI + Python determinístico.
**Fallback:** DeepSeek de raciocínio via OpenCode ou Claude Sonnet autorizado + mesmo harness Python.
**Adaptadores candidatos:** `codex_local; opencode_local / claude_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Ler dados autorizados e criar lançamentos propostos;sem escrituração oficial autônoma. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. DRE gerencial
2. plano de contas
3. conciliação
4. competência
5. centros de custo
6. fechamento
7. auditoria documental
8. controle de duplicidade
9. variação orçamentária
10. qualidade contábil

**Ferramentas candidatas:** Planilhas; SQL; Python; extratos redigidos; ERP leitura.

**KPIs e metas iniciais propostas:**

- 100% divergências explicadas ou abertas
- 0 dupla contagem
- ≥99% reconciliação em fixture

**Testes de qualificação (não executados):**

- `NLE-PLUTUS-CTRL-Q01`: Conciliar 100 lançamentos sintéticos.
- `NLE-PLUTUS-CTRL-Q02`: detectar pagamento duplicado.
- `NLE-PLUTUS-CTRL-Q03`: separar caixa de competência.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
