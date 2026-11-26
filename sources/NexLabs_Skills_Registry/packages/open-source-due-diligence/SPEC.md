# open-source-due-diligence

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige open source due diligence; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Relatório de proveniência, licença e maturidade.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: TOB; sem importação automática.

## Competências rastreadas (10)
- community analysis
- dependency mapping
- documentation quality
- fork comparison
- GitHub maturity analysis
- license analysis
- maintainer health
- release cadence
- software supply chain research
- vulnerability history

## Avaliação
- Cenário de pacote: Rejeitar dependência sem licença e origem verificável.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-PROMETHEUS-OSINT-Q01, NLE-PROMETHEUS-OSINT-Q02, NLE-PROMETHEUS-OSINT-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

