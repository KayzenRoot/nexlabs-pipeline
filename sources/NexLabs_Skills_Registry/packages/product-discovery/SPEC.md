# product-discovery

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige product discovery; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Hipóteses e evidência de demanda com critério de parada.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: MKT; sem importação automática.

## Competências rastreadas (25)
- análise concorrencial
- análise de tendências
- blue ocean strategy
- business model canvas
- competitive moats
- discovery
- experimentos
- go-to-market
- go-to-market experiments
- hipóteses
- JTBD
- keyword research
- market sizing
- MVP hypotheses
- opportunity mapping
- pesquisa de demanda
- pesquisa de usuário
- priorização
- problem validation
- product analytics
- review mining
- roadmap
- segmentação
- validação de preço
- willingness to pay

## Avaliação
- Cenário de pacote: Não promover hipótese sem evidência suficiente.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HEPHAESTUS-PM-Q01, NLE-HEPHAESTUS-PM-Q02, NLE-HEPHAESTUS-PM-Q03, NLE-MUSES-NICHE-Q01, NLE-MUSES-NICHE-Q02, NLE-MUSES-NICHE-Q03, NLE-PROMETHEUS-BIZ-Q01, NLE-PROMETHEUS-BIZ-Q02, NLE-PROMETHEUS-BIZ-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

