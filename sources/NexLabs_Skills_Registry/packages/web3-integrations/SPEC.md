# web3-integrations

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: HIGH_ASSURANCE

## Contrato
- Gatilho: tarefa autorizada que exige web3 integrations; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Integração wallet/RPC simulada.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (10)
- chain switching
- event decoding
- indexação
- nonce management
- reorg handling
- RPC
- signature domain separation
- transaction simulation
- viem
- wallet connectors

## Avaliação
- Cenário de pacote: Reorg e replay não corrompem estado; sem signing real.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HEPHAESTUS-WINT-Q01, NLE-HEPHAESTUS-WINT-Q02, NLE-HEPHAESTUS-WINT-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

