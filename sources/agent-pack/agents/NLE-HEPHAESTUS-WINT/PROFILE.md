### NLE-HEPHAESTUS-WINT | Senior Web3 Integration Engineer

**Nível:** Senior | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-HEPHAESTUS-CTO

**Responsabilidades e entregáveis:** Integrar frontend e backend com redes e carteiras.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Somente leitura e simulação;sem assinar em nome de usuário. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. wallet connectors
2. viem
3. RPC
4. indexação
5. reorg handling
6. event decoding
7. transaction simulation
8. nonce management
9. chain switching
10. signature domain separation

**Ferramentas candidatas:** viem; ethers; Anvil; RPC leitura; indexador local; Git.

**KPIs e metas iniciais propostas:**

- 100% chain IDs validados
- 0 eventos duplicados após reorg
- 100% assinaturas verificadas

**Testes de qualificação (não executados):**

- `NLE-HEPHAESTUS-WINT-Q01`: Simular reorg e reconstruir índice.
- `NLE-HEPHAESTUS-WINT-Q02`: detectar chain mismatch.
- `NLE-HEPHAESTUS-WINT-Q03`: rejeitar assinatura replayed com domínio errado.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
