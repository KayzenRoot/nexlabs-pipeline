# core-data-quality

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core data quality; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Validar dados, deduplicar e registrar inconsistências.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (5)
- data integrity
- data quality
- deduplicação
- integridade de dados
- qualidade de dados

## Avaliação
- Cenário de pacote: fixture duplicada não pode inflar resultado.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-APOLLO-MKTDA-Q01, NLE-APOLLO-MKTDA-Q02, NLE-APOLLO-MKTDA-Q03, NLE-ARGUS-SWA-Q01, NLE-ARGUS-SWA-Q02, NLE-ARGUS-SWA-Q03, NLE-ATHENA-KM-Q01, NLE-ATHENA-KM-Q02, NLE-ATHENA-KM-Q03, NLE-HEPHAESTUS-DATA-Q01, NLE-HEPHAESTUS-DATA-Q02, NLE-HEPHAESTUS-DATA-Q03, NLE-HEPHAESTUS-INT-Q01, NLE-HEPHAESTUS-INT-Q02, NLE-HEPHAESTUS-INT-Q03, NLE-HERMES-PROS-Q01, NLE-HERMES-PROS-Q02, NLE-HERMES-PROS-Q03, NLE-HERMES-SI-Q01, NLE-HERMES-SI-Q02, NLE-HERMES-SI-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

