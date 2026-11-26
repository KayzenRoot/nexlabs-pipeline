# core-incident-recovery

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core incident recovery; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Classificar incidente, conter e recuperar.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (5)
- business continuity
- disaster recovery
- gestão de incidentes
- incident response
- rollback

## Avaliação
- Cenário de pacote: falha crítica exige escalonamento e prova de restauração.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-ARGUS-CISO-Q01, NLE-ARGUS-CISO-Q02, NLE-ARGUS-CISO-Q03, NLE-ARGUS-ORA-Q01, NLE-ARGUS-ORA-Q02, NLE-ARGUS-ORA-Q03, NLE-ATLAS-AOPS-Q01, NLE-ATLAS-AOPS-Q02, NLE-ATLAS-AOPS-Q03, NLE-ATLAS-COO-Q01, NLE-ATLAS-COO-Q02, NLE-ATLAS-COO-Q03, NLE-ATLAS-IMP-Q01, NLE-ATLAS-IMP-Q02, NLE-ATLAS-IMP-Q03, NLE-HEPHAESTUS-DEVOPS-Q01, NLE-HEPHAESTUS-DEVOPS-Q02, NLE-HEPHAESTUS-DEVOPS-Q03, NLE-HEPHAESTUS-SRE-Q01, NLE-HEPHAESTUS-SRE-Q02, NLE-HEPHAESTUS-SRE-Q03, NLE-ZEUS-CEO-Q01, NLE-ZEUS-CEO-Q02, NLE-ZEUS-CEO-Q03, NLE-ZEUS-CEO-Q04.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

