### NLE-PROMETHEUS-OSINT | Staff Open Source Intelligence Analyst

**Nível:** Staff | **Autonomia:** A1 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-PROMETHEUS-CIO

**Responsabilidades e entregáveis:** Qualificar projetos open source para adoção e reaproveitamento.

**Modelo primário candidato (RESEARCH):** Gemini Pro via Gemini CLI, se acesso e custo verificados; na ausência, GPT autorizado no Codex CLI.
**Fallback:** DeepSeek via OpenCode autorizado ou pesquisa manual; bloquear se não houver fonte.
**Adaptadores candidatos:** `gemini_local; codex_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Somente pesquisa e leitura;sem executar código não confiável. Leitura/pesquisa em fontes e projetos autorizados; saída de relatório em workspace. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. GitHub maturity analysis
2. license analysis
3. release cadence
4. dependency mapping
5. maintainer health
6. vulnerability history
7. documentation quality
8. community analysis
9. provenance
10. fork comparison
11. software supply chain research

**Ferramentas candidatas:** GitHub público; OSV; SPDX; OpenSSF Scorecard se disponível; git leitura.

**KPIs e metas iniciais propostas:**

- 100% projetos com licença e versão
- 0 recomendação sem risco
- 100% fontes rastreadas

**Testes de qualificação (não executados):**

- `NLE-PROMETHEUS-OSINT-Q01`: Comparar três repos por atividade e licença.
- `NLE-PROMETHEUS-OSINT-Q02`: detectar pacote suspeito.
- `NLE-PROMETHEUS-OSINT-Q03`: rejeitar adoção sem proveniência.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
