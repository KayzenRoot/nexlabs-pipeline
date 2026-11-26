# sales-outreach

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige sales outreach; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Cadência e qualificação com opt-out.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: MKT; sem importação automática.

## Competências rastreadas (19)
- agenda
- cadências
- copy B2B
- CRM hygiene
- deliverability
- discovery
- handoff comercial
- lead routing
- mensagens multicanal
- objection handling
- objeções
- opt-out
- personalização
- qualificação assíncrona
- qualificação BANT
- SLA de resposta
- SPF/DKIM/DMARC diagnóstico
- SPICED
- triagem

## Avaliação
- Cenário de pacote: Opt-out bloqueia novo contato; somente drafts.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HERMES-IN-Q01, NLE-HERMES-IN-Q02, NLE-HERMES-IN-Q03, NLE-HERMES-OUT-Q01, NLE-HERMES-OUT-Q02, NLE-HERMES-OUT-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

