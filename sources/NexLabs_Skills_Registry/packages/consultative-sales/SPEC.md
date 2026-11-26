# consultative-sales

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige consultative sales; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Proposta de valor e handoff comercial.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: MKT; sem importação automática.

## Competências rastreadas (20)
- afiliados
- co-selling
- conflito de interesse
- contratos de parceria
- due diligence
- economia de canais
- follow-up
- governança de indicação
- handoff contratual
- mapeamento de parceiros
- MEDDICC
- negociação
- objection handling
- performance de parceiros
- pricing
- procurement
- proposta de valor
- revenda
- stakeholder mapping
- venda consultiva

## Avaliação
- Cenário de pacote: Identificar conflito e obrigação não aprovada.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HERMES-AE-Q01, NLE-HERMES-AE-Q02, NLE-HERMES-AE-Q03, NLE-HERMES-PART-Q01, NLE-HERMES-PART-Q02, NLE-HERMES-PART-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

