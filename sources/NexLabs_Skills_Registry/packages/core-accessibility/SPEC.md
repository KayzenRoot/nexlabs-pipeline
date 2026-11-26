# core-accessibility

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core accessibility; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Validar acessibilidade conforme tipo de artefato.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (4)
- acessibilidade
- acessibilidade textual
- alt text
- WCAG

## Avaliação
- Cenário de pacote: fixture com barreira de acessibilidade deve falhar.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-APOLLO-DES-Q01, NLE-APOLLO-DES-Q02, NLE-APOLLO-DES-Q03, NLE-HEPHAESTUS-FE-Q01, NLE-HEPHAESTUS-FE-Q02, NLE-HEPHAESTUS-FE-Q03, NLE-HEPHAESTUS-UX-Q01, NLE-HEPHAESTUS-UX-Q02, NLE-HEPHAESTUS-UX-Q03, NLE-MUSES-DQA-Q01, NLE-MUSES-DQA-Q02, NLE-MUSES-DQA-Q03, NLE-MUSES-EDES-Q01, NLE-MUSES-EDES-Q02, NLE-MUSES-EDES-Q03, NLE-MUSES-EDITOR-Q01, NLE-MUSES-EDITOR-Q02, NLE-MUSES-EDITOR-Q03, NLE-MUSES-ID-Q01, NLE-MUSES-ID-Q02, NLE-MUSES-ID-Q03, NLE-MUSES-ILL-Q01, NLE-MUSES-ILL-Q02, NLE-MUSES-ILL-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

