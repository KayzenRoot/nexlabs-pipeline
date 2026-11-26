# security-governance

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: HIGH_ASSURANCE

## Contrato
- Gatilho: tarefa autorizada que exige security governance; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Modelo de ameaça, riscos e controles independentes.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: TOB; sem importação automática.

## Competências rastreadas (14)
- approval integrity
- budget compliance
- control testing
- evidence sampling
- fraud indicators
- IAM
- incident taxonomy
- process audit
- secrets lifecycle
- security architecture
- security governance
- segregation of duties
- supply chain security
- Zero Trust

## Avaliação
- Cenário de pacote: Bloquear autoaprovação e privilégio excessivo.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-ARGUS-CISO-Q01, NLE-ARGUS-CISO-Q02, NLE-ARGUS-CISO-Q03, NLE-ARGUS-ORA-Q01, NLE-ARGUS-ORA-Q02, NLE-ARGUS-ORA-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

