# innovation-strategy

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige innovation strategy; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Radar tecnológico e priorização de experimentos.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (18)
- AI evaluation
- API maturity
- benchmark review
- build vs buy
- commercial validation
- innovation portfolio
- knowledge transfer
- license verification
- option value
- R&D strategy
- research prioritization
- technology radar
- technology readiness
- technology scouting
- trend analysis
- TRL
- vendor lock-in
- Web3 ecosystem research

## Avaliação
- Cenário de pacote: Não promover tecnologia sem evidência e licença.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-PROMETHEUS-CIO-Q01, NLE-PROMETHEUS-CIO-Q02, NLE-PROMETHEUS-CIO-Q03, NLE-PROMETHEUS-TECH-Q01, NLE-PROMETHEUS-TECH-Q02, NLE-PROMETHEUS-TECH-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

