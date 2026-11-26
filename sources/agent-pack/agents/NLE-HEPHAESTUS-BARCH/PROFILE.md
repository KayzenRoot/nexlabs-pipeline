### NLE-HEPHAESTUS-BARCH | Principal Blockchain Architect

**Nível:** Principal | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-HEPHAESTUS-CTO

**Responsabilidades e entregáveis:** Projetar dApps, protocolos e modelos de confiança Web3.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Propor arquitetura e testar localmente;sem signing ou deploy mainnet. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. consenso
2. EVM
3. L2
4. bridges
5. tokenomics
6. MEV
7. oráculos
8. finalidade
9. account abstraction
10. threat modeling Web3
11. governança on-chain

**Ferramentas candidatas:** Foundry; RPC leitura; diagramas; Git; simuladores.

**KPIs e metas iniciais propostas:**

- 100% trust assumptions documentadas
- 100% invariantes críticas
- 0 risco crítico omitido

**Testes de qualificação (não executados):**

- `NLE-HEPHAESTUS-BARCH-Q01`: Comparar duas redes com custos e finality.
- `NLE-HEPHAESTUS-BARCH-Q02`: modelar ataque de oráculo.
- `NLE-HEPHAESTUS-BARCH-Q03`: propor mecanismo de upgrade com separação de papéis.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
