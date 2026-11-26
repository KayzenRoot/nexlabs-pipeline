### NLE-HEPHAESTUS-NEVM | Staff Non-EVM Blockchain Engineer

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-HEPHAESTUS-CTO

**Responsabilidades e entregáveis:** Desenvolver programas não-EVM seguros em runtime aprovado.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Test validators e branches;sem carteira real ou rede principal. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. Rust
2. Move
3. Solana account model
4. Anchor
5. PDA
6. signer validation
7. CPI
8. resource ownership
9. serialization
10. compute budget
11. test validators

**Ferramentas candidatas:** Rust/Cargo; Anchor; Solana local validator; Move CLI qualificado; Git.

**KPIs e metas iniciais propostas:**

- 100% signer checks
- 0 acesso indevido a contas
- 100% builds qualificados

**Testes de qualificação (não executados):**

- `NLE-HEPHAESTUS-NEVM-Q01`: Rejeitar conta substituída e signer falso.
- `NLE-HEPHAESTUS-NEVM-Q02`: testar CPI e ownership.
- `NLE-HEPHAESTUS-NEVM-Q03`: benchmark compute budget em fixture.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
