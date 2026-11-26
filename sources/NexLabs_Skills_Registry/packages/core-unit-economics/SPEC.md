# core-unit-economics

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core unit economics; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Calcular custos, receita e economia unitária com premissas.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (6)
- CAC
- CAC/LTV
- LTV
- margem de contribuição
- payback
- unit economics

## Avaliação
- Cenário de pacote: reconciliar margem e taxas em fixture.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-APOLLO-CMO-Q01, NLE-APOLLO-CMO-Q02, NLE-APOLLO-CMO-Q03, NLE-HERMES-CRO-Q01, NLE-HERMES-CRO-Q02, NLE-HERMES-CRO-Q03, NLE-MUSES-CDPO-Q01, NLE-MUSES-CDPO-Q02, NLE-MUSES-CDPO-Q03, NLE-MUSES-OFFER-Q01, NLE-MUSES-OFFER-Q02, NLE-MUSES-OFFER-Q03, NLE-PLUTUS-UNIT-Q01, NLE-PLUTUS-UNIT-Q02, NLE-PLUTUS-UNIT-Q03, NLE-PROMETHEUS-BIZ-Q01, NLE-PROMETHEUS-BIZ-Q02, NLE-PROMETHEUS-BIZ-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

