# reliability-operations

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige reliability operations; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Runbook, SLO e recuperação de sessão.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: PC; sem importação automática.

## Competências rastreadas (18)
- agent health
- alert routing
- backup restore
- capacity
- capacity metrics
- chaos testing seguro
- configuration drift
- heartbeat scheduling
- Linux
- observabilidade
- observability
- postmortem
- queue backpressure
- run cancellation
- runbooks
- session recovery
- SLI/SLO
- worker isolation

## Avaliação
- Cenário de pacote: Injetar falha e recuperar sem execução duplicada.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-ATLAS-AOPS-Q01, NLE-ATLAS-AOPS-Q02, NLE-ATLAS-AOPS-Q03, NLE-HEPHAESTUS-SRE-Q01, NLE-HEPHAESTUS-SRE-Q02, NLE-HEPHAESTUS-SRE-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

