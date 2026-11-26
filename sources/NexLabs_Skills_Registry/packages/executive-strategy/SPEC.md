# executive-strategy

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: STANDARD

## Contrato
- Gatilho: tarefa autorizada que exige executive strategy; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Plano de prioridades com restrições, responsáveis e decisões.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: PC; sem importação automática.

## Competências rastreadas (28)
- alocação de capital
- análise de dependências
- análise de posicionamento
- análise ROI
- análise SWOT
- avaliação de alternativas
- cenários
- classificação de escopo
- decisão multicritério
- delegação baseada em evidência
- estratégia corporativa
- estratégia de portfólio
- gestão de benefícios
- gestão de ciclo de vida
- gestão de dependências
- gestão de OKRs
- gestão de portfólio
- governança de decisões
- OKRs
- orquestração multiagente
- planejamento estratégico
- planejamento trimestral
- priorização por valor
- resolução de conflitos
- RICE
- roadmap
- vantagem competitiva
- WSJF

## Avaliação
- Cenário de pacote: Detectar conflito de recursos e produzir ordem sem ciclos.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-ATHENA-PORT-Q01, NLE-ATHENA-PORT-Q02, NLE-ATHENA-PORT-Q03, NLE-ATHENA-STR-Q01, NLE-ATHENA-STR-Q02, NLE-ATHENA-STR-Q03, NLE-ZEUS-CEO-Q01, NLE-ZEUS-CEO-Q02, NLE-ZEUS-CEO-Q03, NLE-ZEUS-CEO-Q04.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

