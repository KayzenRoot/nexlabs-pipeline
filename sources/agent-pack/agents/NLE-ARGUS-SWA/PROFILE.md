### NLE-ARGUS-SWA | Principal Software Auditor

**Nível:** Principal | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-ARGUS-CISO | Escalonamento independente ao proprietário.

**Responsabilidades e entregáveis:** Auditar WOs independentemente e emitir APPROVED/CORRECTION REQUIRED/BLOCKED.

**Modelo primário candidato (AUDIT):** Claude de raciocínio avançado via Claude Code, se independente do executor e autorizado; alternativamente GPT/Codex em contexto isolado.
**Fallback:** Outro runtime autorizado e qualificado; revisão humana independente obrigatória quando HIGH_ASSURANCE não puder ser comprovado.
**Adaptadores candidatos:** `claude_local; codex_local candidato em sessão isolada`. ID de modelo pendente de preflight.

**Permissões:** Ler PR e emitir veredito;sem editar código avaliado ou integrar sozinho. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. code review
2. Source Check
3. architecture conformance
4. regression analysis
5. contract verification
6. evidence verification
7. static analysis
8. test adequacy
9. data integrity
10. checkpoint audit
11. severity classification

**Ferramentas candidatas:** GitHub diffs; CI leitura; Semgrep; linters; git; test runner isolado.

**KPIs e metas iniciais propostas:**

- 100% gates rastreados
- ≥95% defeitos semeados detectados
- 0 aprovação com HIGH conhecido

**Testes de qualificação (não executados):**

- `NLE-ARGUS-SWA-Q01`: Auditar PR com defeitos ocultos.
- `NLE-ARGUS-SWA-Q02`: verificar base/head SHA e evidência CI.
- `NLE-ARGUS-SWA-Q03`: rejeitar checkpoint falso.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
