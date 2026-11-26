# b2b-prospecting

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige b2b prospecting; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Leads empresariais qualificados com fontes.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: MKT; sem importação automática.

## Competências rastreadas (16)
- análise de concorrência
- attribution
- CRM analytics
- diagnóstico de presença digital
- enriquecimento permitido
- fit scoring
- ICP
- intenção de compra
- lead scoring
- modelagem de conversão
- personalização por setor
- pesquisa de decisores públicos
- pesquisa de empresas
- prospecção ética
- segmentação B2B
- segmentação firmográfica

## Avaliação
- Cenário de pacote: Deduplicar e excluir dados não autorizados.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HERMES-PROS-Q01, NLE-HERMES-PROS-Q02, NLE-HERMES-PROS-Q03, NLE-HERMES-SI-Q01, NLE-HERMES-SI-Q02, NLE-HERMES-SI-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

