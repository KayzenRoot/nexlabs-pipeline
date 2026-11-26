# core-experiment-design

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core experiment design; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Planejar experimento com métrica e critério de parada.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (7)
- A/B testing
- análise estatística
- experiment design
- experimentação
- sample size
- statistical inference
- teste A/B

## Avaliação
- Cenário de pacote: resultado enviesado não pode ser declarado causal.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-APOLLO-CMO-Q01, NLE-APOLLO-CMO-Q02, NLE-APOLLO-CMO-Q03, NLE-APOLLO-CRM-Q01, NLE-APOLLO-CRM-Q02, NLE-APOLLO-CRM-Q03, NLE-APOLLO-CRO-Q01, NLE-APOLLO-CRO-Q02, NLE-APOLLO-CRO-Q03, NLE-APOLLO-PAID-Q01, NLE-APOLLO-PAID-Q02, NLE-APOLLO-PAID-Q03, NLE-HEPHAESTUS-PERF-Q01, NLE-HEPHAESTUS-PERF-Q02, NLE-HEPHAESTUS-PERF-Q03, NLE-HERMES-OUT-Q01, NLE-HERMES-OUT-Q02, NLE-HERMES-OUT-Q03, NLE-MUSES-CDPO-Q01, NLE-MUSES-CDPO-Q02, NLE-MUSES-CDPO-Q03, NLE-POSEIDON-QR-Q01, NLE-POSEIDON-QR-Q02, NLE-POSEIDON-QR-Q03, NLE-PROMETHEUS-CIO-Q01, NLE-PROMETHEUS-CIO-Q02, NLE-PROMETHEUS-CIO-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

