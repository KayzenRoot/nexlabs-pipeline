# technology-strategy

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige technology strategy; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: ADR e arquitetura com alternativas e trade-offs.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OA; sem importação automática.

## Competências rastreadas (19)
- arquitetura empresarial
- arquitetura evolutiva
- arquitetura hexagonal
- build vs buy
- consistência distribuída
- contratos API
- DDD
- engenharia de confiabilidade
- estratégia tecnológica
- event-driven
- gestão de custos cloud
- gestão de dívida
- gestão de risco técnico
- governança de SDLC
- liderança técnica
- modelagem de dados
- modular monolith
- planejamento de plataforma
- trade-offs CAP

## Avaliação
- Cenário de pacote: Rejeitar arquitetura incompatível com restrição aprovada.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HEPHAESTUS-ARCH-Q01, NLE-HEPHAESTUS-ARCH-Q02, NLE-HEPHAESTUS-ARCH-Q03, NLE-HEPHAESTUS-CTO-Q01, NLE-HEPHAESTUS-CTO-Q02, NLE-HEPHAESTUS-CTO-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

