# ux-design

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige ux design; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Design system, fluxos e auditoria de acessibilidade.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: VER; sem importação automática.

## Competências rastreadas (9)
- design mobile
- design responsivo
- design systems
- fluxos de interação
- handoff a engenharia
- heurísticas
- prototipagem
- testes de usabilidade
- tokens

## Avaliação
- Cenário de pacote: Detectar contraste, foco e navegação deficientes.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-HEPHAESTUS-UX-Q01, NLE-HEPHAESTUS-UX-Q02, NLE-HEPHAESTUS-UX-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

