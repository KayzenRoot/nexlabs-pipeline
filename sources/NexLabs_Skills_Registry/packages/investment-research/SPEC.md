# investment-research

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: HIGH_ASSURANCE

## Contrato
- Gatilho: tarefa autorizada que exige investment research; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Tese, alocação hipotética e riscos.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (9)
- asset allocation
- benchmark selection
- due diligence
- investment governance
- investment thesis
- portfolio construction
- regime analysis
- research prioritization
- scenario analysis

## Avaliação
- Cenário de pacote: Rejeitar recomendação sem dados e sem benchmark.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-POSEIDON-CIO-Q01, NLE-POSEIDON-CIO-Q02, NLE-POSEIDON-CIO-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

