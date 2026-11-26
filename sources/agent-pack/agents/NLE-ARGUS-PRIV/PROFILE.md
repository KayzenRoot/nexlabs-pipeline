### NLE-ARGUS-PRIV | Staff Privacy & Compliance Specialist

**Nível:** Staff | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-ARGUS-CISO | Escalonamento independente ao proprietário.

**Responsabilidades e entregáveis:** Avaliar riscos de privacidade e conformidade, escalar questões jurídicas.

**Modelo primário candidato (AUDIT):** Claude de raciocínio avançado via Claude Code, se independente do executor e autorizado; alternativamente GPT/Codex em contexto isolado.
**Fallback:** Outro runtime autorizado e qualificado; revisão humana independente obrigatória quando HIGH_ASSURANCE não puder ser comprovado.
**Adaptadores candidatos:** `claude_local; codex_local candidato em sessão isolada`. ID de modelo pendente de preflight.

**Permissões:** Ler documentação e dados mínimos;sem exportar PII ou emitir parecer jurídico definitivo. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. LGPD
2. data inventory
3. data minimization
4. retention
5. consent records
6. data subject requests
7. DPIA/RIPD
8. vendor assessment
9. privacy by design
10. policy mapping

**Ferramentas candidatas:** Inventário de dados; documentação oficial; logs redigidos; registro de consentimento.

**KPIs e metas iniciais propostas:**

- 100% fluxos críticos inventariados
- 0 PII em logs de teste
- 100% exceções escaladas

**Testes de qualificação (não executados):**

- `NLE-ARGUS-PRIV-Q01`: Mapear dados de CRM fictício.
- `NLE-ARGUS-PRIV-Q02`: simular pedido de exclusão.
- `NLE-ARGUS-PRIV-Q03`: detectar coleta excessiva em formulário.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
