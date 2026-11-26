# core-capacity-cost

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core capacity cost; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Planejar capacidade e limites de recursos.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (6)
- budget enforcement
- capacity planning
- controle de custos de IA
- gestão de capacidade
- planejamento de capacidade
- quota management

## Avaliação
- Cenário de pacote: quota esgotada bloqueia nova execução.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-ATHENA-PMO-Q01, NLE-ATHENA-PMO-Q02, NLE-ATHENA-PMO-Q03, NLE-ATHENA-PORT-Q01, NLE-ATHENA-PORT-Q02, NLE-ATHENA-PORT-Q03, NLE-ATLAS-COO-Q01, NLE-ATLAS-COO-Q02, NLE-ATLAS-COO-Q03, NLE-HEPHAESTUS-PERF-Q01, NLE-HEPHAESTUS-PERF-Q02, NLE-HEPHAESTUS-PERF-Q03, NLE-PLUTUS-FINOPS-Q01, NLE-PLUTUS-FINOPS-Q02, NLE-PLUTUS-FINOPS-Q03, NLE-ZEUS-CEO-Q01, NLE-ZEUS-CEO-Q02, NLE-ZEUS-CEO-Q03, NLE-ZEUS-CEO-Q04.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

