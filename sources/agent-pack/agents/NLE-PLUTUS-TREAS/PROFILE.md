### NLE-PLUTUS-TREAS | Senior Treasury Specialist

**Nível:** Senior | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-PLUTUS-CFO

**Responsabilidades e entregáveis:** Prever liquidez e preparar plano de pagamentos e recebimentos.

**Modelo primário candidato (QUANT):** GPT de raciocínio avançado disponível no Codex CLI + Python determinístico.
**Fallback:** DeepSeek de raciocínio via OpenCode ou Claude Sonnet autorizado + mesmo harness Python.
**Adaptadores candidatos:** `codex_local; opencode_local / claude_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Apenas propostas de movimentação;sem acesso de pagamento ou transferência. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. cash flow
2. liquidez
3. contas a pagar
4. contas a receber
5. aging
6. projeção de caixa
7. conciliação bancária
8. calendário financeiro
9. capital de giro
10. cenários de stress

**Ferramentas candidatas:** Planilhas; ERP leitura; extratos redigidos; Python.

**KPIs e metas iniciais propostas:**

- 100% vencimentos monitorados
- 100% saldos com fonte
- 0 ordens financeiras

**Testes de qualificação (não executados):**

- `NLE-PLUTUS-TREAS-Q01`: Projetar caixa por 13 semanas.
- `NLE-PLUTUS-TREAS-Q02`: detectar insuficiência de liquidez.
- `NLE-PLUTUS-TREAS-Q03`: rejeitar instrução de PIX não autorizado.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
