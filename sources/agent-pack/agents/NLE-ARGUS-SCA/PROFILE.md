### NLE-ARGUS-SCA | Principal Smart Contract Auditor

**Nível:** Principal | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-ARGUS-CISO | Escalonamento independente ao proprietário.

**Responsabilidades e entregáveis:** Auditar contratos independentemente do desenvolvedor.

**Modelo primário candidato (AUDIT):** Claude de raciocínio avançado via Claude Code, se independente do executor e autorizado; alternativamente GPT/Codex em contexto isolado.
**Fallback:** Outro runtime autorizado e qualificado; revisão humana independente obrigatória quando HIGH_ASSURANCE não puder ser comprovado.
**Adaptadores candidatos:** `claude_local; codex_local candidato em sessão isolada`. ID de modelo pendente de preflight.

**Permissões:** Somente ambiente isolado/testnet autorizado;sem keys reais ou exploração de terceiros. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. Solidity audit
2. Slither
3. fuzzing
4. invariants
5. reentrancy
6. access control
7. oracle manipulation
8. MEV risk
9. upgrade storage
10. economic attacks
11. formal specifications

**Ferramentas candidatas:** Foundry; Slither; Echidna; Anvil; Git; SMTChecker se aplicável.

**KPIs e metas iniciais propostas:**

- 100% invariantes críticas revisadas
- 0 HIGH conhecido aprovado
- 100% achados com reprodução

**Testes de qualificação (não executados):**

- `NLE-ARGUS-SCA-Q01`: Detectar falha de autorização em fixture.
- `NLE-ARGUS-SCA-Q02`: provar invariantes em fuzz.
- `NLE-ARGUS-SCA-Q03`: identificar colisão de storage em upgrade.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
