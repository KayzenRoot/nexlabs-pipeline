# core-source-evidence

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core source evidence; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Verificar fontes, registrar proveniência e produzir evidências.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (9)
- controle de fontes
- evidence verification
- provenance
- proveniência
- source triangulation
- source validation
- source verification
- triangulação de fontes
- validação de fonte

## Avaliação
- Cenário de pacote: fonte falsa e referência quebrada devem ser detectadas.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-ARGUS-SWA-Q01, NLE-ARGUS-SWA-Q02, NLE-ARGUS-SWA-Q03, NLE-ATHENA-KM-Q01, NLE-ATHENA-KM-Q02, NLE-ATHENA-KM-Q03, NLE-HEPHAESTUS-REL-Q01, NLE-HEPHAESTUS-REL-Q02, NLE-HEPHAESTUS-REL-Q03, NLE-HERMES-PROS-Q01, NLE-HERMES-PROS-Q02, NLE-HERMES-PROS-Q03, NLE-MUSES-NICHE-Q01, NLE-MUSES-NICHE-Q02, NLE-MUSES-NICHE-Q03, NLE-POSEIDON-EQ-Q01, NLE-POSEIDON-EQ-Q02, NLE-POSEIDON-EQ-Q03, NLE-PROMETHEUS-MARKET-Q01, NLE-PROMETHEUS-MARKET-Q02, NLE-PROMETHEUS-MARKET-Q03, NLE-PROMETHEUS-OSINT-Q01, NLE-PROMETHEUS-OSINT-Q02, NLE-PROMETHEUS-OSINT-Q03, NLE-PROMETHEUS-TECH-Q01, NLE-PROMETHEUS-TECH-Q02, NLE-PROMETHEUS-TECH-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

