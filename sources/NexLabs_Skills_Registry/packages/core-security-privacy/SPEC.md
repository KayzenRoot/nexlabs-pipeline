# core-security-privacy

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige core security privacy; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Aplicar menor privilégio e proteger dados/segredos.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (8)
- data minimization
- least privilege
- LGPD
- privacy by design
- prompt injection defense
- secret handling
- secret management
- secret redaction

## Avaliação
- Cenário de pacote: tentativa de acesso indevido deve ser negada.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-APOLLO-CRM-Q01, NLE-APOLLO-CRM-Q02, NLE-APOLLO-CRM-Q03, NLE-APOLLO-MKTDA-Q01, NLE-APOLLO-MKTDA-Q02, NLE-APOLLO-MKTDA-Q03, NLE-ARGUS-AISEC-Q01, NLE-ARGUS-AISEC-Q02, NLE-ARGUS-AISEC-Q03, NLE-ARGUS-CISO-Q01, NLE-ARGUS-CISO-Q02, NLE-ARGUS-CISO-Q03, NLE-ARGUS-PRIV-Q01, NLE-ARGUS-PRIV-Q02, NLE-ARGUS-PRIV-Q03, NLE-HEPHAESTUS-AI-Q01, NLE-HEPHAESTUS-AI-Q02, NLE-HEPHAESTUS-AI-Q03, NLE-HEPHAESTUS-AUTO-Q01, NLE-HEPHAESTUS-AUTO-Q02, NLE-HEPHAESTUS-AUTO-Q03, NLE-HEPHAESTUS-DEVOPS-Q01, NLE-HEPHAESTUS-DEVOPS-Q02, NLE-HEPHAESTUS-DEVOPS-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

