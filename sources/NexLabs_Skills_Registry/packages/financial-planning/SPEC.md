# financial-planning

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige financial planning; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Modelo de projeção, margem e sensibilidade.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (16)
- break-even
- budgeting
- capital budgeting
- churn
- cohort analysis
- customer profitability
- driver-based modeling
- economia de marketplace
- financial storytelling
- model audit
- pricing
- rolling forecast
- scenario planning
- sensitivity
- taxas de pagamento
- variance analysis

## Avaliação
- Cenário de pacote: Recalcular fórmula e cenários com dados sintéticos.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-PLUTUS-FPA-Q01, NLE-PLUTUS-FPA-Q02, NLE-PLUTUS-FPA-Q03, NLE-PLUTUS-UNIT-Q01, NLE-PLUTUS-UNIT-Q02, NLE-PLUTUS-UNIT-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

