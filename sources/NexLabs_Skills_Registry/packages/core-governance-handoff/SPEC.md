# core-governance-handoff

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core governance handoff; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Registrar decisão, escopo, evidência e handoff.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (6)
- ADR
- checkpoint delta
- Context Lock
- Definition of Done
- Evidence Bundle
- Source Pack

## Avaliação
- Cenário de pacote: aprovação ausente ou SHA divergente impede avanço.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HEPHAESTUS-ARCH-Q01, NLE-HEPHAESTUS-ARCH-Q02, NLE-HEPHAESTUS-ARCH-Q03, NLE-HEPHAESTUS-PM-Q01, NLE-HEPHAESTUS-PM-Q02, NLE-HEPHAESTUS-PM-Q03, NLE-HEPHAESTUS-REL-Q01, NLE-HEPHAESTUS-REL-Q02, NLE-HEPHAESTUS-REL-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

