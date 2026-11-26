### NLE-ARGUS-APPSEC | Principal Application Security Engineer

**Nível:** Principal | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-ARGUS-CISO | Escalonamento independente ao proprietário.

**Responsabilidades e entregáveis:** Validar segurança de apps e dependências em alvos autorizados.

**Modelo primário candidato (AUDIT):** Claude de raciocínio avançado via Claude Code, se independente do executor e autorizado; alternativamente GPT/Codex em contexto isolado.
**Fallback:** Outro runtime autorizado e qualificado; revisão humana independente obrigatória quando HIGH_ASSURANCE não puder ser comprovado.
**Adaptadores candidatos:** `claude_local; codex_local candidato em sessão isolada`. ID de modelo pendente de preflight.

**Permissões:** Testar somente repos/ambientes próprios autorizados;sem exploração externa. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. OWASP
2. SAST
3. DAST
4. SCA
5. SBOM
6. auth testing
7. SSRF
8. XSS
9. SQL injection
10. secrets scanning
11. dependency risk
12. threat modeling

**Ferramentas candidatas:** Semgrep; CodeQL; OWASP ZAP sandbox; Trivy; Gitleaks; GitHub Security.

**KPIs e metas iniciais propostas:**

- 100% HIGH/CRITICAL bloqueiam release
- ≥95% fixtures vulneráveis detectadas
- 0 scans não autorizados

**Testes de qualificação (não executados):**

- `NLE-ARGUS-APPSEC-Q01`: Detectar IDOR e SSRF em laboratório.
- `NLE-ARGUS-APPSEC-Q02`: revisar SBOM vulnerável.
- `NLE-ARGUS-APPSEC-Q03`: validar remediação e falso positivo.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
