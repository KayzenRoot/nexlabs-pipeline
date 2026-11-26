# blockchain-architecture

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: HIGH_ASSURANCE

## Contrato
- Gatilho: tarefa autorizada que exige blockchain architecture; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Arquitetura blockchain e análise de confiança.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: TOB; sem importação automática.

## Competências rastreadas (11)
- account abstraction
- bridges
- consenso
- EVM
- finalidade
- governança on-chain
- L2
- MEV
- oráculos
- threat modeling Web3
- tokenomics

## Avaliação
- Cenário de pacote: Identificar riscos de bridge, finalidade e oráculo.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HEPHAESTUS-BARCH-Q01, NLE-HEPHAESTUS-BARCH-Q02, NLE-HEPHAESTUS-BARCH-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

