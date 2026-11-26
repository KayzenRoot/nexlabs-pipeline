# core-risk-analysis

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core risk analysis; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Identificar riscos, impacto e mitigação sem autoaprovação.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (5)
- gestão de riscos
- risk acceptance
- risk budgeting
- risk register
- threat modeling

## Avaliação
- Cenário de pacote: risco crítico sem tratamento bloqueia avanço.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-ARGUS-APPSEC-Q01, NLE-ARGUS-APPSEC-Q02, NLE-ARGUS-APPSEC-Q03, NLE-ARGUS-CISO-Q01, NLE-ARGUS-CISO-Q02, NLE-ARGUS-CISO-Q03, NLE-ARGUS-ORA-Q01, NLE-ARGUS-ORA-Q02, NLE-ARGUS-ORA-Q03, NLE-ATHENA-PMO-Q01, NLE-ATHENA-PMO-Q02, NLE-ATHENA-PMO-Q03, NLE-HEPHAESTUS-ARCH-Q01, NLE-HEPHAESTUS-ARCH-Q02, NLE-HEPHAESTUS-ARCH-Q03, NLE-POSEIDON-CIO-Q01, NLE-POSEIDON-CIO-Q02, NLE-POSEIDON-CIO-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

