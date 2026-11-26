# meta-ads-analysis

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: HIGH_ASSURANCE

## Contrato
- Gatilho: tarefa autorizada que exige meta ads analysis; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Auditoria e proposta de campanhas Meta.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: MKT, META; sem importação automática.

## Competências rastreadas (13)
- advertising policy
- attribution
- audience research
- budget pacing
- campaign architecture
- Conversions API
- creative fatigue
- creative testing
- event deduplication
- incrementality
- Pixel
- retargeting consentido
- ROAS

## Avaliação
- Cenário de pacote: Com orçamento zero, nenhuma alteração em campanha real.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-APOLLO-META-Q01, NLE-APOLLO-META-Q02, NLE-APOLLO-META-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

