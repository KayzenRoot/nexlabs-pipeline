# crypto-research

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: HIGH_ASSURANCE

## Contrato
- Gatilho: tarefa autorizada que exige crypto research; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Relatório cripto e on-chain com fontes.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: CG, BIN; sem importação automática.

## Competências rastreadas (33)
- ABI decoding
- AMMs
- bridge risk
- chain attribution
- contract verification
- data lineage
- due diligence
- event logs
- exchange inflows
- exchange risk
- FDV
- flows
- gas analysis
- governance
- impermanent loss
- lending
- liquidation
- liquidez
- liquidity pools
- market cap
- narrative analysis
- oracle risk
- protocol fundamentals
- reorgs
- scam indicators
- smart contract due diligence
- staking
- tokenomics
- TVL
- TVL methodology
- vesting
- wallet clustering com ressalvas
- yield decomposition

## Avaliação
- Cenário de pacote: Detectar dados antigos, token incorreto e risco de protocolo.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-POSEIDON-CHAIN-Q01, NLE-POSEIDON-CHAIN-Q02, NLE-POSEIDON-CHAIN-Q03, NLE-POSEIDON-CRYPTO-Q01, NLE-POSEIDON-CRYPTO-Q02, NLE-POSEIDON-CRYPTO-Q03, NLE-POSEIDON-DEFI-Q01, NLE-POSEIDON-DEFI-Q02, NLE-POSEIDON-DEFI-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

