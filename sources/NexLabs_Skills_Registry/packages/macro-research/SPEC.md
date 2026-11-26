# macro-research

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige macro research; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Relatório macro e sentimento com timestamp.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (21)
- bias analysis
- commodities
- cross-asset correlation
- economic releases
- entity resolution
- event extraction
- FX drivers
- GDP
- inflation
- labor market
- monetary policy
- news classification
- revision tracking
- rumor detection
- scenario analysis
- sentiment scoring
- signal decay
- social listening permitido
- source reliability
- time alignment
- yield curve

## Avaliação
- Cenário de pacote: Detectar fonte falsa e viés temporal.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-POSEIDON-MACRO-Q01, NLE-POSEIDON-MACRO-Q02, NLE-POSEIDON-MACRO-Q03, NLE-POSEIDON-SENT-Q01, NLE-POSEIDON-SENT-Q02, NLE-POSEIDON-SENT-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

