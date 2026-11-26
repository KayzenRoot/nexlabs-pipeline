# service-operations

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige service operations; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Plano de SLA, suporte e customer health.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (27)
- adoption metrics
- API diagnostics
- churn signals
- customer communication
- customer education
- customer health
- customer operations
- delivery governance
- escalation
- expectation management
- incident classification
- incident coordination
- knowledge base
- log analysis
- network diagnostics
- onboarding
- QBR
- queue management
- renewal preparation
- reproduction
- resource optimization
- retention
- secure support
- service operations
- SLA
- SOP
- troubleshooting

## Avaliação
- Cenário de pacote: Incidente crítico escalado; sem revelar dados de outro cliente.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-ATLAS-COO-Q01, NLE-ATLAS-COO-Q02, NLE-ATLAS-COO-Q03, NLE-ATLAS-CS-Q01, NLE-ATLAS-CS-Q02, NLE-ATLAS-CS-Q03, NLE-ATLAS-SUP-Q01, NLE-ATLAS-SUP-Q02, NLE-ATLAS-SUP-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

