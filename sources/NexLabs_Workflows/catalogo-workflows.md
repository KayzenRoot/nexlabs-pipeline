# Catálogo de workflows NLE-WF-PLAN-001

Status: PROPOSED / não ativado. As skills listadas são elegíveis, não carregadas ou comprovadas. Todos os passos têm efeito externo negado por padrão. O dono é accountable, não recebe permissões adicionais. A aprovação humana não amplia a permissão do agente; ação externa passa por serviço autorizado e read-back.

## NLE-WF-GOV-01 · Estratégia e OKRs

**Responsável:** NLE-ZEUS-CEO | **Despacho:** NLE-ZEUS-CEO | **Revisor:** NLE-ARGUS-ORA | **Risco:** STANDARD | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Semanal e mensal  
**Entradas:** Resultados, caixa e capacidade

### Etapas

1. **NLE-ATHENA-STR (A3)**: converter objetivos em OKRs. Skills elegíveis: executive-strategy.

2. **NLE-ATHENA-PORT (A2)**: priorizar portfólio. Skills elegíveis: core-capacity-cost, executive-strategy.

3. **NLE-PLUTUS-CFO (A3)**: avaliar orçamento. Skills elegíveis: corporate-finance.

4. **NLE-ZEUS-CEO (A3)**: consolidar decisões. Skills elegíveis: core-capacity-cost, core-incident-recovery, executive-strategy.

**Entrega:** Plano estratégico versionado  
**KPIs:** OKRs com responsável e prazo >=95%; gasto novo=0  
**Teste específico (NOT_RUN):** Conflito de recursos deve bloquear compromisso inviável  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-GOV-02 · Triagem e despacho

**Responsável:** NLE-ATHENA-PMO | **Despacho:** NLE-ATHENA-PMO | **Revisor:** NLE-ARGUS-ORA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Nova tarefa  
**Entradas:** Briefing, política e locks

### Etapas

1. **NLE-ATHENA-BA (A2)**: classificar requisitos. Skills elegíveis: business-requirements.

2. **NLE-ATHENA-PMO (A3)**: resolver dependências e prioridade. Skills elegíveis: core-capacity-cost, core-risk-analysis, project-governance.

3. **NLE-ZEUS-CEO (A3)**: delegar conforme capacidade. Skills elegíveis: core-capacity-cost, core-incident-recovery, executive-strategy.

**Entrega:** Issue com dono, dependências e limites  
**KPIs:** 100% tarefas com dono; duplicatas=0  
**Teste específico (NOT_RUN):** Evento duplicado e dependência circular não criam execução  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-GOV-03 · Conhecimento e fontes

**Responsável:** NLE-ATHENA-KM | **Despacho:** NLE-ATHENA-PMO | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** Mudança de fonte ou entrega  
**Entradas:** Documentos autorizados e hashes

### Etapas

1. **NLE-ATHENA-KM (A2)**: indexar e recuperar fontes. Skills elegíveis: core-data-quality, core-source-evidence, knowledge-retrieval.

2. **NLE-HEPHAESTUS-DATA (A2)**: validar metadados e isolamento. Skills elegíveis: core-data-quality, data-engineering.

3. **NLE-ATHENA-PEX (A2)**: analisar lacunas. Skills elegíveis: process-excellence.

**Entrega:** Índice versionado e trilha de fontes  
**KPIs:** 100% fontes críticas identificadas; vazamento=0  
**Teste específico (NOT_RUN):** Documento de outro cliente não é recuperado  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-GOV-04 · Melhoria de processos

**Responsável:** NLE-ATHENA-PEX | **Despacho:** NLE-ATHENA-PMO | **Revisor:** NLE-ARGUS-ORA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Semanal  
**Entradas:** Logs, tempos, falhas

### Etapas

1. **NLE-ATHENA-PEX (A2)**: diagnosticar gargalo. Skills elegíveis: process-excellence.

2. **NLE-HEPHAESTUS-AUTO (A2)**: propor automação. Skills elegíveis: core-reliable-workflows, core-security-privacy, workflow-automation.

3. **NLE-ATHENA-PMO (A3)**: planejar experimento. Skills elegíveis: core-capacity-cost, core-risk-analysis, project-governance.

**Entrega:** Proposta e teste de processo  
**KPIs:** Tempo de ciclo comparado ao baseline; regressões críticas=0  
**Teste específico (NOT_RUN):** Falha no experimento restaura fluxo anterior  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-GOV-05 · Qualificação de agente e skill

**Responsável:** NLE-ATLAS-AOPS | **Despacho:** NLE-ATLAS-AOPS | **Revisor:** NLE-ARGUS-AISEC | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Nova versão ou mudança de modelo  
**Entradas:** Manifesto, hash, licenças, testes

### Etapas

1. **NLE-PROMETHEUS-OSINT (A1)**: verificar origem. Skills elegíveis: core-source-evidence, open-source-due-diligence.

2. **NLE-HEPHAESTUS-AI (A2)**: testar modelo e skill. Skills elegíveis: core-security-privacy, core-tool-budget, llm-engineering.

3. **NLE-ATLAS-AOPS (A3)**: validar runtime. Skills elegíveis: core-incident-recovery, core-reliable-workflows, reliability-operations.

4. **NLE-PLUTUS-FINOPS (A3)**: validar quota. Skills elegíveis: ai-finops, core-capacity-cost, core-tool-budget.

**Entrega:** Evidence Bundle G01-G05 e SR01-SR06  
**KPIs:** 100% gates; nota >=90/100; HIGH=0  
**Teste específico (NOT_RUN):** Skill adulterada ou executor incompatível não é ativado  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-RES-01 · Pesquisa de mercado

**Responsável:** NLE-PROMETHEUS-CIO | **Despacho:** NLE-PROMETHEUS-CIO | **Revisor:** NLE-ATHENA-STR | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Semanal  
**Entradas:** Hipóteses e fontes públicas

### Etapas

1. **NLE-PROMETHEUS-MARKET (A1)**: dimensionar mercado. Skills elegíveis: core-source-evidence, market-intelligence.

2. **NLE-PROMETHEUS-BIZ (A2)**: identificar problemas e oportunidades. Skills elegíveis: core-unit-economics, product-discovery.

3. **NLE-PROMETHEUS-CIO (A3)**: ranquear hipóteses. Skills elegíveis: core-experiment-design, innovation-strategy.

**Entrega:** Dossiê de oportunidades  
**KPIs:** 100% claims materiais com fonte; premissas explícitas  
**Teste específico (NOT_RUN):** Demanda sem evidência é marcada não validada  
**Próximos candidatos condicionais:** NLE-WF-RES-03

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-RES-02 · Radar tecnológico e due diligence

**Responsável:** NLE-PROMETHEUS-CIO | **Despacho:** NLE-PROMETHEUS-CIO | **Revisor:** NLE-ARGUS-AISEC | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Semanal ou nova tecnologia  
**Entradas:** Repositórios e docs oficiais

### Etapas

1. **NLE-PROMETHEUS-TECH (A1)**: comparar capacidade. Skills elegíveis: core-source-evidence, innovation-strategy.

2. **NLE-PROMETHEUS-OSINT (A1)**: avaliar licença e origem. Skills elegíveis: core-source-evidence, open-source-due-diligence.

3. **NLE-ATLAS-PROC (A2)**: comparar custos. Skills elegíveis: procurement.

**Entrega:** Relatório de adoção ou rejeição  
**KPIs:** 100% candidatos com licença/custo conhecidos ou bloqueados  
**Teste específico (NOT_RUN):** Dependência sem licença não entra em adoção  
**Próximos candidatos condicionais:** NLE-WF-RES-03

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-RES-03 · Validação de novo produto

**Responsável:** NLE-PROMETHEUS-CIO | **Despacho:** NLE-PROMETHEUS-CIO | **Revisor:** NLE-ATHENA-PORT | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Oportunidade aprovada  
**Entradas:** Dossiê e limite de recursos

### Etapas

1. **NLE-PROMETHEUS-BIZ (A2)**: formular teste de demanda. Skills elegíveis: core-unit-economics, product-discovery.

2. **NLE-PROMETHEUS-PROTO (A2)**: criar PoC isolada. Skills elegíveis: rapid-prototyping.

3. **NLE-HEPHAESTUS-PM (A2)**: definir escopo. Skills elegíveis: core-governance-handoff, product-discovery.

4. **NLE-PLUTUS-UNIT (A2)**: simular margem. Skills elegíveis: core-unit-economics, financial-planning.

**Entrega:** Go/no-go proposto e evidências  
**KPIs:** Hipóteses testadas; custo incremental=0  
**Teste específico (NOT_RUN):** PoC sem demanda não avança automaticamente  
**Próximos candidatos condicionais:** NLE-WF-ENG-01, NLE-WF-DIG-01

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SAL-01 · ICP e prospecção B2B

**Responsável:** NLE-HERMES-CRO | **Despacho:** NLE-HERMES-CRO | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** Diário em dias úteis  
**Entradas:** ICP aprovado e fontes empresariais permitidas

### Etapas

1. **NLE-HERMES-PROS (A1)**: pesquisar empresas. Skills elegíveis: b2b-prospecting, core-data-quality, core-source-evidence.

2. **NLE-HERMES-SI (A2)**: validar fit e deduplicar. Skills elegíveis: b2b-prospecting, core-data-quality.

3. **NLE-HERMES-CRO (A3)**: priorizar carteira. Skills elegíveis: core-unit-economics, sales-strategy.

**Entrega:** Fila de leads com fonte e finalidade  
**KPIs:** 100% origem rastreável; duplicatas=0  
**Teste específico (NOT_RUN):** Contato suprimido ou dado sensível é excluído da fila  
**Próximos candidatos condicionais:** NLE-WF-SAL-02

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SAL-02 · Outreach personalizado

**Responsável:** NLE-HERMES-CRO | **Despacho:** NLE-HERMES-CRO | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Lead qualificado  
**Entradas:** Lead permitido e oferta

### Etapas

1. **NLE-HERMES-OUT (A2)**: preparar abordagem individual. Skills elegíveis: core-experiment-design, sales-outreach.

2. **NLE-APOLLO-COPY (A2)**: revisar mensagem. Skills elegíveis: content-strategy.

3. **NLE-HERMES-CRO (A3)**: validar cadência e relevância. Skills elegíveis: core-unit-economics, sales-strategy.

**Entrega:** Rascunhos e fila de envio aprovado  
**KPIs:** Taxa de resposta e opt-out; envios sem autorização=0  
**Teste específico (NOT_RUN):** Opt-out, limite ou ausência de base válida impede envio  
**Próximos candidatos condicionais:** NLE-WF-SAL-04

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SAL-03 · Inbound e qualificação

**Responsável:** NLE-HERMES-IN | **Despacho:** NLE-HERMES-IN | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Lead recebido por canal autorizado  
**Entradas:** Mensagem e consentimentos aplicáveis

### Etapas

1. **NLE-HERMES-IN (A3)**: classificar intenção e urgência. Skills elegíveis: sales-outreach.

2. **NLE-HERMES-SI (A2)**: verificar duplicidade e fit. Skills elegíveis: b2b-prospecting, core-data-quality.

3. **NLE-HERMES-SE (A2)**: avaliar necessidade técnica. Skills elegíveis: technical-presales.

**Entrega:** Lead qualificado ou encerrado  
**KPIs:** Tempo de primeira triagem; 100% opt-outs respeitados  
**Teste específico (NOT_RUN):** Webhook repetido não duplica lead; resposta externa só por política  
**Próximos candidatos condicionais:** NLE-WF-SAL-04

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SAL-04 · Discovery e pré-venda

**Responsável:** NLE-HERMES-CRO | **Despacho:** NLE-HERMES-CRO | **Revisor:** NLE-HEPHAESTUS-CTO | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Lead aceito  
**Entradas:** Briefing e restrições do cliente

### Etapas

1. **NLE-HERMES-SE (A2)**: mapear necessidade e estimativa. Skills elegíveis: technical-presales.

2. **NLE-ATHENA-BA (A2)**: documentar requisitos. Skills elegíveis: business-requirements.

3. **NLE-HEPHAESTUS-ARCH (A2)**: validar arquitetura. Skills elegíveis: core-governance-handoff, core-risk-analysis, technology-strategy.

4. **NLE-PLUTUS-UNIT (A2)**: estimar margem. Skills elegíveis: core-unit-economics, financial-planning.

**Entrega:** Escopo preliminar e faixa de esforço  
**KPIs:** 100% premissas registradas; margem prevista  
**Teste específico (NOT_RUN):** Requisito ambíguo impede preço fechado  
**Próximos candidatos condicionais:** NLE-WF-SAL-05

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SAL-05 · Proposta, negociação e contrato

**Responsável:** NLE-HERMES-CRO | **Despacho:** NLE-HERMES-CRO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Discovery aprovado  
**Entradas:** Escopo, preço e condições

### Etapas

1. **NLE-HERMES-AE (A2)**: redigir proposta. Skills elegíveis: consultative-sales.

2. **NLE-PLUTUS-FPA (A2)**: validar cenários. Skills elegíveis: financial-planning.

3. **NLE-ARGUS-LEGAL (A1)**: emitir parecer de risco. Skills elegíveis: legal-research.

4. **NLE-HERMES-CRO (A3)**: consolidar condições. Skills elegíveis: core-unit-economics, sales-strategy.

**Entrega:** Proposta e contrato para assinatura humana  
**KPIs:** Win rate; margem; compromissos não autorizados=0  
**Teste específico (NOT_RUN):** Mudança de escopo ou preço invalida aprovação  
**Próximos candidatos condicionais:** NLE-WF-SAL-07

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SAL-06 · Parcerias e canais

**Responsável:** NLE-HERMES-CRO | **Despacho:** NLE-HERMES-CRO | **Revisor:** NLE-ARGUS-LEGAL | **Risco:** STANDARD | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Semanal ou inbound  
**Entradas:** Candidato e critérios comerciais

### Etapas

1. **NLE-HERMES-PART (A2)**: avaliar parceria. Skills elegíveis: consultative-sales.

2. **NLE-PROMETHEUS-MARKET (A1)**: comparar mercado. Skills elegíveis: core-source-evidence, market-intelligence.

3. **NLE-PLUTUS-UNIT (A2)**: simular comissão. Skills elegíveis: core-unit-economics, financial-planning.

**Entrega:** Proposta de parceria sem compromisso  
**KPIs:** Pipeline de parceiros; margem incremental  
**Teste específico (NOT_RUN):** Comissão não aprovada não é contratada  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SAL-07 · Handoff para entrega

**Responsável:** NLE-ATLAS-COO | **Despacho:** NLE-ATLAS-COO | **Revisor:** NLE-ARGUS-ORA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Contrato efetivamente aprovado  
**Entradas:** Contrato, escopo, responsável e aceite

### Etapas

1. **NLE-HERMES-AE (A2)**: registrar termos aprovados. Skills elegíveis: consultative-sales.

2. **NLE-ATHENA-PMO (A3)**: planejar projeto. Skills elegíveis: core-capacity-cost, core-risk-analysis, project-governance.

3. **NLE-ATLAS-IMP (A3)**: preparar onboarding. Skills elegíveis: core-incident-recovery, customer-implementation.

4. **NLE-ATLAS-CS (A3)**: definir plano de sucesso. Skills elegíveis: service-operations.

**Entrega:** Projeto e onboarding rastreáveis  
**KPIs:** 100% contratos com handoff; escopo íntegro  
**Teste específico (NOT_RUN):** Contrato não assinado bloqueia início contratado  
**Próximos candidatos condicionais:** NLE-WF-ENG-01, NLE-WF-OPS-01

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-01 · Source Pack e arquitetura

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-SWA | **Risco:** STANDARD | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Novo projeto autorizado  
**Entradas:** Escopo, checkpoint se existente e decisões

### Etapas

1. **NLE-HEPHAESTUS-PM (A2)**: definir produto. Skills elegíveis: core-governance-handoff, product-discovery.

2. **NLE-ATHENA-BA (A2)**: refinar requisitos. Skills elegíveis: business-requirements.

3. **NLE-HEPHAESTUS-ARCH (A2)**: propor arquitetura e ADRs. Skills elegíveis: core-governance-handoff, core-risk-analysis, technology-strategy.

4. **NLE-HEPHAESTUS-REL (A2)**: versionar Source Pack. Skills elegíveis: core-governance-handoff, core-source-evidence, engineering-governance.

**Entrega:** Source Pack, DoD e baseline  
**KPIs:** 100% docs necessários; decisões conflitantes=0  
**Teste específico (NOT_RUN):** Checkpoint e ADR conflitantes bloqueiam implementação  
**Próximos candidatos condicionais:** NLE-WF-ENG-02

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-02 · Work Order e Context Lock

**Responsável:** NLE-ATHENA-PMO | **Despacho:** NLE-ATHENA-PMO | **Revisor:** NLE-ARGUS-SWA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Incremento necessário  
**Entradas:** Fontes canônicas e Git base

### Etapas

1. **NLE-HEPHAESTUS-ARCH (A2)**: definir arquitetura e critérios. Skills elegíveis: core-governance-handoff, core-risk-analysis, technology-strategy.

2. **NLE-HEPHAESTUS-REL (A2)**: gerar lock e fingerprints. Skills elegíveis: core-governance-handoff, core-source-evidence, engineering-governance.

3. **NLE-ATHENA-PMO (A3)**: validar dependências. Skills elegíveis: core-capacity-cost, core-risk-analysis, project-governance.

**Entrega:** WO com base SHA e preflight  
**KPIs:** 100% locks válidos e critérios testáveis  
**Teste específico (NOT_RUN):** Mudança crítica marca STALE e bloqueia execução  
**Próximos candidatos condicionais:** NLE-WF-ENG-03, NLE-WF-ENG-04, NLE-WF-ENG-05, NLE-WF-ENG-06, NLE-WF-ENG-07, NLE-WF-ENG-08, NLE-WF-ENG-09

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-03 · Frontend e design system

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-SWA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** WO autorizado  
**Entradas:** Design, contratos e lock

### Etapas

1. **NLE-HEPHAESTUS-UX (A2)**: projetar UI acessível. Skills elegíveis: core-accessibility, ux-design.

2. **NLE-HEPHAESTUS-FE (A2)**: implementar em branch isolada. Skills elegíveis: core-accessibility, frontend-engineering.

3. **NLE-HEPHAESTUS-QA (A2)**: validar comportamento. Skills elegíveis: software-testing.

**Entrega:** Diff, screenshots e testes  
**KPIs:** AC atendidos; regressões críticas=0  
**Teste específico (NOT_RUN):** Navegação teclado e estados de erro testados  
**Próximos candidatos condicionais:** NLE-WF-ENG-10

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-04 · Backend e integrações

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-APPSEC | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** WO autorizado  
**Entradas:** Contratos API, requisitos e lock

### Etapas

1. **NLE-HEPHAESTUS-BE (A2)**: implementar serviços. Skills elegíveis: backend-engineering, core-reliable-workflows.

2. **NLE-HEPHAESTUS-INT (A2)**: integrar APIs. Skills elegíveis: api-integrations, core-data-quality, core-reliable-workflows.

3. **NLE-HEPHAESTUS-DATA (A2)**: validar migrações e dados. Skills elegíveis: core-data-quality, data-engineering.

4. **NLE-HEPHAESTUS-QA (A2)**: testar contratos. Skills elegíveis: software-testing.

**Entrega:** Código, testes e migração ensaiada  
**KPIs:** Contratos aprovados; integridade preservada  
**Teste específico (NOT_RUN):** Retry não duplica gravação; rollback/roll-forward testado  
**Próximos candidatos condicionais:** NLE-WF-ENG-10

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-05 · Mobile Android/iOS

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-SWA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** WO autorizado  
**Entradas:** Design e plataformas elegíveis

### Etapas

1. **NLE-HEPHAESTUS-MOB (A2)**: implementar app. Skills elegíveis: mobile-engineering.

2. **NLE-HEPHAESTUS-UX (A2)**: validar experiência. Skills elegíveis: core-accessibility, ux-design.

3. **NLE-HEPHAESTUS-QA (A2)**: testar dispositivos disponíveis. Skills elegíveis: software-testing.

**Entrega:** Build e evidências por plataforma  
**KPIs:** AC e testes por plataforma comprovada  
**Teste específico (NOT_RUN):** Plataforma sem toolchain fica BLOCKED, não simulada como aprovada  
**Próximos candidatos condicionais:** NLE-WF-ENG-10

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-06 · IA, RAG e automação

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-AISEC | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** WO autorizado  
**Entradas:** Dataset permitido, modelo e orçamento

### Etapas

1. **NLE-HEPHAESTUS-AI (A2)**: implementar pipeline e evals. Skills elegíveis: core-security-privacy, core-tool-budget, llm-engineering.

2. **NLE-HEPHAESTUS-AUTO (A2)**: integrar workflow. Skills elegíveis: core-reliable-workflows, core-security-privacy, workflow-automation.

3. **NLE-HEPHAESTUS-INT (A2)**: validar contratos. Skills elegíveis: api-integrations, core-data-quality, core-reliable-workflows.

**Entrega:** Pipeline com avaliação e limites  
**KPIs:** Qualidade versus baseline; quota respeitada  
**Teste específico (NOT_RUN):** Prompt injection e indisponibilidade do modelo falham fechadas  
**Próximos candidatos condicionais:** NLE-WF-ENG-10

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-07 · Web3 arquitetura e integração

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-SCA | **Risco:** HIGH_ASSURANCE | **Gate:** INTERNAL_ONLY

**Gatilho:** WO Web3 autorizado  
**Entradas:** Rede candidata e threat model

### Etapas

1. **NLE-HEPHAESTUS-BARCH (A2)**: projetar protocolo. Skills elegíveis: blockchain-architecture.

2. **NLE-HEPHAESTUS-WINT (A2)**: integrar RPC e wallet mock. Skills elegíveis: web3-integrations.

3. **NLE-HEPHAESTUS-INT (A2)**: testar contratos externos. Skills elegíveis: api-integrations, core-data-quality, core-reliable-workflows.

**Entrega:** PoC local e modelo de ameaças  
**KPIs:** 100% fronteiras de confiança testadas  
**Teste específico (NOT_RUN):** RPC divergente ou assinatura não autorizada bloqueia operação  
**Próximos candidatos condicionais:** NLE-WF-ENG-08, NLE-WF-ENG-09

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-08 · Smart contracts EVM

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-SCA | **Risco:** HIGH_ASSURANCE | **Gate:** INTERNAL_ONLY

**Gatilho:** WO EVM autorizado  
**Entradas:** Especificação e invariantes

### Etapas

1. **NLE-HEPHAESTUS-EVM (A2)**: implementar em ambiente local. Skills elegíveis: solidity-engineering.

2. **NLE-HEPHAESTUS-QA (A2)**: testar propriedades. Skills elegíveis: software-testing.

3. **NLE-HEPHAESTUS-PERF (A2)**: medir gas e desempenho. Skills elegíveis: core-capacity-cost, core-experiment-design, performance-engineering.

**Entrega:** Contratos, fuzz/invariantes e evidências  
**KPIs:** Invariantes críticas 100%; HIGH=0  
**Teste específico (NOT_RUN):** Reentrância, permissões e conservação de ativos testadas em laboratório  
**Próximos candidatos condicionais:** NLE-WF-ENG-10

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-09 · Smart contracts não EVM

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-SCA | **Risco:** HIGH_ASSURANCE | **Gate:** INTERNAL_ONLY

**Gatilho:** WO não EVM autorizado  
**Entradas:** VM, rede e modelo de contas

### Etapas

1. **NLE-HEPHAESTUS-NEVM (A2)**: implementar programas locais. Skills elegíveis: non-evm-engineering.

2. **NLE-HEPHAESTUS-BARCH (A2)**: validar modelo de estado. Skills elegíveis: blockchain-architecture.

3. **NLE-HEPHAESTUS-QA (A2)**: testar propriedades. Skills elegíveis: software-testing.

**Entrega:** Programa, testes e relatório  
**KPIs:** Invariantes críticas 100%; HIGH=0  
**Teste específico (NOT_RUN):** Conta maliciosa e replay falham sem alteração de estado  
**Próximos candidatos condicionais:** NLE-WF-ENG-10

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-10 · QA, performance e Evidence Bundle

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-SWA | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** Diff pronto  
**Entradas:** Base/head SHA e AC

### Etapas

1. **NLE-HEPHAESTUS-QA (A2)**: rodar suites. Skills elegíveis: software-testing.

2. **NLE-HEPHAESTUS-PERF (A2)**: medir regressões. Skills elegíveis: core-capacity-cost, core-experiment-design, performance-engineering.

3. **NLE-HEPHAESTUS-REL (A2)**: consolidar evidências e checkpoint delta. Skills elegíveis: core-governance-handoff, core-source-evidence, engineering-governance.

**Entrega:** Evidence Bundle e PR candidata  
**KPIs:** 100% gates aplicáveis comprovados  
**Teste específico (NOT_RUN):** Teste ausente, skip artificial ou evidência de SHA errado bloqueiam  
**Próximos candidatos condicionais:** NLE-WF-ENG-11

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-11 · PR, auditoria e integração

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-SWA | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Evidence Bundle pronto  
**Entradas:** PR, checks, fontes e diff

### Etapas

1. **NLE-HEPHAESTUS-REL (A2)**: preparar PR e delta. Skills elegíveis: core-governance-handoff, core-source-evidence, engineering-governance.

2. **NLE-ARGUS-APPSEC (A2)**: avaliar segurança. Skills elegíveis: application-security, core-risk-analysis.

3. **NLE-HEPHAESTUS-CTO (A3)**: solicitar decisão de integração. Skills elegíveis: technology-strategy.

**Entrega:** Veredito, checkpoint aprovado e integração autorizada  
**KPIs:** HIGH=0; 100% merges com gates  
**Teste específico (NOT_RUN):** Head alterado invalida aprovação; sem bypass ou force push  
**Próximos candidatos condicionais:** NLE-WF-ENG-12

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-12 · Release, deploy e rollback

**Responsável:** NLE-HEPHAESTUS-CTO | **Despacho:** NLE-HEPHAESTUS-CTO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Versão integrada  
**Entradas:** Artefato, migração e plano de recuperação

### Etapas

1. **NLE-HEPHAESTUS-DEVOPS (A3)**: ensaiar pipeline. Skills elegíveis: core-incident-recovery, core-security-privacy, release-infrastructure.

2. **NLE-HEPHAESTUS-SRE (A3)**: validar monitoramento e rollback. Skills elegíveis: core-incident-recovery, reliability-operations.

3. **NLE-ATLAS-IMP (A3)**: validar implantação. Skills elegíveis: core-incident-recovery, customer-implementation.

**Entrega:** Release candidato e smoke tests  
**KPIs:** 100% smoke; recuperação ensaiada; gastos novos=0  
**Teste específico (NOT_RUN):** Deploy parcial falha fechada e aciona recuperação aprovada  
**Próximos candidatos condicionais:** NLE-WF-OPS-01

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-ENG-13 · Manutenção e correções

**Responsável:** NLE-ATLAS-COO | **Despacho:** NLE-ATLAS-COO | **Revisor:** NLE-ARGUS-SWA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Bug, alerta ou SLA  
**Entradas:** Ticket, logs sanitizados e checkpoint

### Etapas

1. **NLE-ATLAS-SUP (A3)**: reproduzir problema. Skills elegíveis: service-operations.

2. **NLE-HEPHAESTUS-SRE (A3)**: diagnosticar. Skills elegíveis: core-incident-recovery, reliability-operations.

3. **NLE-ATHENA-PMO (A3)**: abrir incremento de correção. Skills elegíveis: core-capacity-cost, core-risk-analysis, project-governance.

4. **NLE-HEPHAESTUS-REL (A2)**: registrar evidência. Skills elegíveis: core-governance-handoff, core-source-evidence, engineering-governance.

**Entrega:** WO corretivo e diagnóstico  
**KPIs:** MTTR; recorrência; regressões=0  
**Teste específico (NOT_RUN):** Não reproduzido não é marcado corrigido  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-DIG-01 · Pesquisa de nichos e oferta

**Responsável:** NLE-MUSES-CDPO | **Despacho:** NLE-MUSES-CDPO | **Revisor:** NLE-ATHENA-PORT | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Semanal  
**Entradas:** Pesquisa de mercado e margem

### Etapas

1. **NLE-MUSES-NICHE (A1)**: pesquisar demanda. Skills elegíveis: core-source-evidence, product-discovery.

2. **NLE-MUSES-OFFER (A2)**: modelar oferta e preço. Skills elegíveis: core-unit-economics, product-offer.

3. **NLE-PLUTUS-UNIT (A2)**: calcular cenários. Skills elegíveis: core-unit-economics, financial-planning.

4. **NLE-MUSES-CDPO (A3)**: selecionar proposta. Skills elegíveis: core-experiment-design, core-unit-economics, product-offer.

**Entrega:** Brief de produto e funil  
**KPIs:** Margem prevista e premissas verificáveis  
**Teste específico (NOT_RUN):** Sem evidência de demanda não publicar  
**Próximos candidatos condicionais:** NLE-WF-DIG-02

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-DIG-02 · Produção editorial de e-books

**Responsável:** NLE-MUSES-CDPO | **Despacho:** NLE-MUSES-CDPO | **Revisor:** NLE-MUSES-DQA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Brief aprovado  
**Entradas:** Público, fontes e objetivos

### Etapas

1. **NLE-MUSES-AUTHOR (A2)**: escrever conteúdo original. Skills elegíveis: longform-writing.

2. **NLE-MUSES-ID (A2)**: desenhar aprendizagem. Skills elegíveis: core-accessibility, instructional-design.

3. **NLE-MUSES-EDITOR (A2)**: revisar fatos. Skills elegíveis: core-accessibility, longform-writing.

4. **NLE-MUSES-ILL (A2)**: criar ilustrações. Skills elegíveis: core-accessibility, creative-production.

5. **NLE-MUSES-EDES (A2)**: diagramar PDF. Skills elegíveis: core-accessibility, editorial-production.

**Entrega:** PDF e fontes licenciadas  
**KPIs:** 100% checklist editorial; erros críticos=0  
**Teste específico (NOT_RUN):** Referência falsa ou imagem sem direitos impede entrega  
**Próximos candidatos condicionais:** NLE-WF-DIG-03

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-DIG-03 · Funil e assets comerciais

**Responsável:** NLE-MUSES-CDPO | **Despacho:** NLE-MUSES-CDPO | **Revisor:** NLE-ARGUS-PRIV | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Produto revisado  
**Entradas:** Produto, preço proposto e público

### Etapas

1. **NLE-MUSES-OFFER (A2)**: definir principal, bump, upsell e downsell. Skills elegíveis: core-unit-economics, product-offer.

2. **NLE-APOLLO-COPY (A2)**: redigir copy. Skills elegíveis: content-strategy.

3. **NLE-APOLLO-DES (A2)**: criar peças. Skills elegíveis: core-accessibility, creative-production.

4. **NLE-APOLLO-CRO (A2)**: projetar landing. Skills elegíveis: conversion-optimization, core-experiment-design.

5. **NLE-MUSES-ECOM (A2)**: preparar checkout. Skills elegíveis: core-reliable-workflows, digital-commerce.

**Entrega:** Pacote de funil em rascunho  
**KPIs:** 100% preços consistentes; claims comprovados  
**Teste específico (NOT_RUN):** Preço divergente ou promessa enganosa bloqueia  
**Próximos candidatos condicionais:** NLE-WF-DIG-04

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-DIG-04 · Cakto cadastro e homologação

**Responsável:** NLE-MUSES-CDPO | **Despacho:** NLE-MUSES-CDPO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Funil pronto  
**Entradas:** Artefatos, hashes, escopos API

### Etapas

1. **NLE-MUSES-ECOM (A2)**: preparar cadastro e validar contrato oficial. Skills elegíveis: core-reliable-workflows, digital-commerce.

2. **NLE-MUSES-DQA (A2)**: testar checkout e entrega mock. Skills elegíveis: core-accessibility, digital-product-testing.

3. **NLE-PLUTUS-CTRL (A2)**: validar conciliação prevista. Skills elegíveis: financial-controllership.

**Entrega:** Configuração aprovada e prova de entrega  
**KPIs:** 100% links e arquivos; compra real não autorizada=0  
**Teste específico (NOT_RUN):** Webhook duplicado não libera duas vezes; staging indisponível usa mock  
**Próximos candidatos condicionais:** NLE-WF-DIG-05, NLE-WF-MKT-01

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-DIG-05 · Venda, entrega e reembolso

**Responsável:** NLE-ATLAS-COO | **Despacho:** NLE-ATLAS-COO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Evento de pedido  
**Entradas:** Webhook autenticado e estado de pedido

### Etapas

1. **NLE-MUSES-ECOM (A2)**: normalizar evento e preparar entitlement. Skills elegíveis: core-reliable-workflows, digital-commerce.

2. **NLE-ATLAS-IMP (A3)**: operar entrega interna permitida. Skills elegíveis: core-incident-recovery, customer-implementation.

3. **NLE-ATLAS-CS (A3)**: triar suporte. Skills elegíveis: service-operations.

4. **NLE-PLUTUS-CTRL (A2)**: conciliar. Skills elegíveis: financial-controllership.

**Entrega:** Ledger de pedido e comprovante de entrega  
**KPIs:** Entrega correta; divergências e reembolsos rastreados  
**Teste específico (NOT_RUN):** Evento fora de ordem não reabre acesso indevido; reembolso financeiro exige humano  
**Próximos candidatos condicionais:** NLE-WF-FIN-01

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-01 · Estratégia, marca e calendário

**Responsável:** NLE-APOLLO-CMO | **Despacho:** NLE-APOLLO-CMO | **Revisor:** NLE-ARGUS-PRIV | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Semanal  
**Entradas:** Ofertas, público, dados de desempenho

### Etapas

1. **NLE-APOLLO-BRAND (A2)**: definir identidade. Skills elegíveis: marketing-strategy.

2. **NLE-APOLLO-CONTENT (A2)**: planejar conteúdo. Skills elegíveis: content-strategy.

3. **NLE-APOLLO-SOC (A3)**: distribuir formatos. Skills elegíveis: social-governance.

4. **NLE-APOLLO-CMO (A3)**: priorizar campanhas. Skills elegíveis: core-experiment-design, core-unit-economics, marketing-strategy.

**Entrega:** Calendário e brief de campanha  
**KPIs:** 100% peças com objetivo e canal  
**Teste específico (NOT_RUN):** Claim sem evidência retorna para revisão  
**Próximos candidatos condicionais:** NLE-WF-MKT-02, NLE-WF-MKT-09, NLE-WF-MKT-10, NLE-WF-MKT-11, NLE-WF-MKT-12, NLE-WF-MKT-13

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-02 · Fábrica de criativos

**Responsável:** NLE-APOLLO-CMO | **Despacho:** NLE-APOLLO-CMO | **Revisor:** NLE-APOLLO-BRAND | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Brief ou teste solicitado  
**Entradas:** Identidade, oferta e formatos

### Etapas

1. **NLE-APOLLO-COPY (A2)**: redigir variações. Skills elegíveis: content-strategy.

2. **NLE-APOLLO-DES (A2)**: gerar criativos. Skills elegíveis: core-accessibility, creative-production.

3. **NLE-APOLLO-VID (A2)**: editar vídeo. Skills elegíveis: creative-production.

4. **NLE-APOLLO-CONTENT (A2)**: validar narrativa. Skills elegíveis: content-strategy.

**Entrega:** Assets com versão e direitos  
**KPIs:** 100% formatos e direitos; CTR medido após publicação  
**Teste específico (NOT_RUN):** Asset protegido sem licença é rejeitado  
**Próximos candidatos condicionais:** NLE-WF-MKT-03, NLE-WF-MKT-04, NLE-WF-MKT-05, NLE-WF-MKT-06, NLE-WF-MKT-07, NLE-WF-MKT-08

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-03 · Instagram

**Responsável:** NLE-APOLLO-SOC | **Despacho:** NLE-APOLLO-SOC | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Calendário e janela aprovada  
**Entradas:** Criativo, legenda e conta permitida

### Etapas

1. **NLE-APOLLO-IG (A3)**: adaptar conteúdo, preparar publicação e medir. Skills elegíveis: instagram-content.

2. **NLE-APOLLO-SOC (A3)**: validar frequência. Skills elegíveis: social-governance.

**Entrega:** Post aprovado ou rascunho e métricas  
**KPIs:** Publicações verificadas; saves e cliques  
**Teste específico (NOT_RUN):** Permissão ausente não publica; timeout reconcilia ID  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-04 · Facebook e comunidades

**Responsável:** NLE-APOLLO-SOC | **Despacho:** NLE-APOLLO-SOC | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Calendário aprovado  
**Entradas:** Assets, página e regras de comunidade

### Etapas

1. **NLE-APOLLO-FB (A3)**: preparar posts de página e sugestões para grupos. Skills elegíveis: facebook-content.

2. **NLE-APOLLO-SOC (A3)**: validar frequência e contexto. Skills elegíveis: social-governance.

**Entrega:** Post de página autorizado ou rascunho manual de grupo  
**KPIs:** Engajamento e cliques; spam=0  
**Teste específico (NOT_RUN):** Grupo sem caminho autorizado não publica automaticamente  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-05 · TikTok

**Responsável:** NLE-APOLLO-SOC | **Despacho:** NLE-APOLLO-SOC | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Calendário aprovado  
**Entradas:** Vídeo, direitos e consentimentos exigidos

### Etapas

1. **NLE-APOLLO-TT (A3)**: adaptar roteiro e vídeo, preparar draft e metadados. Skills elegíveis: tiktok-content.

2. **NLE-APOLLO-VID (A2)**: validar direitos de áudio. Skills elegíveis: creative-production.

**Entrega:** Draft ou post autorizado  
**KPIs:** Retenção, cliques e status de publicação  
**Teste específico (NOT_RUN):** Sem consentimento explícito exigido ou auditoria do app, não publicar publicamente  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-06 · Pinterest

**Responsável:** NLE-APOLLO-SOC | **Despacho:** NLE-APOLLO-SOC | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Calendário aprovado  
**Entradas:** Pin, board, URL e escopo

### Etapas

1. **NLE-APOLLO-PIN (A3)**: otimizar pin e preparar publicação. Skills elegíveis: pinterest-content.

2. **NLE-APOLLO-SOC (A3)**: validar repetição. Skills elegíveis: social-governance.

**Entrega:** Pin autorizado e ID externo  
**KPIs:** Outbound clicks, saves; duplicatas=0  
**Teste específico (NOT_RUN):** Board incorreto ou escopo ausente bloqueia  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-07 · YouTube

**Responsável:** NLE-APOLLO-SOC | **Despacho:** NLE-APOLLO-SOC | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Calendário aprovado  
**Entradas:** Vídeo, thumbnail, título e direitos

### Etapas

1. **NLE-APOLLO-YT (A3)**: otimizar metadados e preparar upload. Skills elegíveis: youtube-content.

2. **NLE-APOLLO-VID (A2)**: validar mídia. Skills elegíveis: creative-production.

**Entrega:** Vídeo draft ou publicado autorizado  
**KPIs:** Retenção, CTR thumbnail; direitos comprovados  
**Teste específico (NOT_RUN):** Conta ou licença de mídia não validada bloqueia  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-08 · LinkedIn B2B

**Responsável:** NLE-APOLLO-SOC | **Despacho:** NLE-APOLLO-SOC | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Calendário aprovado  
**Entradas:** Conteúdo técnico e ICP

### Etapas

1. **NLE-APOLLO-LI (A2)**: preparar post e análise B2B. Skills elegíveis: linkedin-content.

2. **NLE-HERMES-CRO (A3)**: priorizar mensagem comercial. Skills elegíveis: core-unit-economics, sales-strategy.

**Entrega:** Rascunho ou publicação por serviço autorizado  
**KPIs:** Leads atribuíveis e engajamento qualificado  
**Teste específico (NOT_RUN):** Agente A2 não publica nem envia mensagens diretamente  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-09 · SEO, GEO e aquisição orgânica

**Responsável:** NLE-APOLLO-CMO | **Despacho:** NLE-APOLLO-CMO | **Revisor:** NLE-ARGUS-SWA | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Semanal  
**Entradas:** Site, Search Console autorizado e conteúdo

### Etapas

1. **NLE-APOLLO-SEO (A2)**: auditar e propor melhorias. Skills elegíveis: search-optimization.

2. **NLE-APOLLO-CONTENT (A2)**: planejar páginas. Skills elegíveis: content-strategy.

3. **NLE-HEPHAESTUS-FE (A2)**: preparar alterações em WO. Skills elegíveis: core-accessibility, frontend-engineering.

**Entrega:** Backlog SEO e evidências  
**KPIs:** Impressões, CTR e tráfego qualificado  
**Teste específico (NOT_RUN):** Mudanças de site seguem ENG; sem cloaking  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-10 · CRM e ciclo de vida

**Responsável:** NLE-APOLLO-CMO | **Despacho:** NLE-APOLLO-CMO | **Revisor:** NLE-ARGUS-PRIV | **Risco:** ELEVATED | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Evento de CRM ou revisão diária  
**Entradas:** Consentimentos, opt-outs e segmentos

### Etapas

1. **NLE-APOLLO-CRM (A3)**: preparar segmentação e mensagens. Skills elegíveis: core-experiment-design, core-security-privacy, crm-lifecycle.

2. **NLE-HERMES-IN (A3)**: triar respostas. Skills elegíveis: sales-outreach.

3. **NLE-APOLLO-COPY (A2)**: revisar copy. Skills elegíveis: content-strategy.

**Entrega:** Campanha autorizada e lista de supressão  
**KPIs:** Conversão e opt-out; mensagens indevidas=0  
**Teste específico (NOT_RUN):** Opt-out concorrente revoga envio pendente  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-11 · Meta Ads

**Responsável:** NLE-APOLLO-CMO | **Despacho:** NLE-APOLLO-CMO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Brief ou revisão diária  
**Entradas:** Conta permitida, métricas e orçamento

### Etapas

1. **NLE-APOLLO-META (A2)**: analisar e preparar campanha/alterações. Skills elegíveis: meta-ads-analysis.

2. **NLE-APOLLO-DES (A2)**: preparar criativos. Skills elegíveis: core-accessibility, creative-production.

3. **NLE-APOLLO-MKTDA (A2)**: validar medição. Skills elegíveis: core-data-quality, core-security-privacy, marketing-measurement.

4. **NLE-PLUTUS-UNIT (A2)**: avaliar CAC e margem. Skills elegíveis: core-unit-economics, financial-planning.

**Entrega:** Plano de campanha ou change set sem ativação  
**KPIs:** CPA, ROAS, margem; gasto sem autorização=0  
**Teste específico (NOT_RUN):** Qualquer ativação, mudança de verba ou targeting fora do escopo bloqueia  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-12 · Google Ads

**Responsável:** NLE-APOLLO-CMO | **Despacho:** NLE-APOLLO-CMO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Brief ou revisão diária  
**Entradas:** Conta, keywords, conversões e orçamento

### Etapas

1. **NLE-APOLLO-GOOG (A2)**: preparar campanha e validar request em mock/teste. Skills elegíveis: google-ads-analysis.

2. **NLE-APOLLO-SEO (A2)**: revisar intenção. Skills elegíveis: search-optimization.

3. **NLE-APOLLO-MKTDA (A2)**: validar conversões. Skills elegíveis: core-data-quality, core-security-privacy, marketing-measurement.

4. **NLE-PLUTUS-UNIT (A2)**: avaliar margem. Skills elegíveis: core-unit-economics, financial-planning.

**Entrega:** Campanha candidata e diagnóstico  
**KPIs:** CPA, ROAS, termos irrelevantes; gasto indevido=0  
**Teste específico (NOT_RUN):** validate_only indisponível exige mock; não ativa produção  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-13 · TikTok Ads e Pinterest Ads

**Responsável:** NLE-APOLLO-CMO | **Despacho:** NLE-APOLLO-CMO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Experimento aprovado para análise  
**Entradas:** Hipótese, criativos e políticas

### Etapas

1. **NLE-APOLLO-PAID (A2)**: preparar experimentos. Skills elegíveis: core-experiment-design, emerging-paid-media.

2. **NLE-APOLLO-TT (A3)**: adaptar criativo. Skills elegíveis: tiktok-content.

3. **NLE-APOLLO-PIN (A3)**: adaptar pin. Skills elegíveis: pinterest-content.

4. **NLE-PLUTUS-UNIT (A2)**: simular custos. Skills elegíveis: core-unit-economics, financial-planning.

**Entrega:** Plano experimental por plataforma  
**KPIs:** CPA, margem e tamanho de amostra  
**Teste específico (NOT_RUN):** Sem orçamento humano ou integração qualificada permanece rascunho  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-MKT-14 · Mensuração e CRO

**Responsável:** NLE-APOLLO-CMO | **Despacho:** NLE-APOLLO-CMO | **Revisor:** NLE-ARGUS-PRIV | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Diário e semanal  
**Entradas:** Eventos e pedidos conciliados

### Etapas

1. **NLE-APOLLO-MKTDA (A2)**: deduplicar eventos e atribuição. Skills elegíveis: core-data-quality, core-security-privacy, marketing-measurement.

2. **NLE-APOLLO-CRO (A2)**: formular teste. Skills elegíveis: conversion-optimization, core-experiment-design.

3. **NLE-PLUTUS-UNIT (A2)**: avaliar contribuição. Skills elegíveis: core-unit-economics, financial-planning.

**Entrega:** Dashboard e hipótese de otimização  
**KPIs:** Receita conciliada; conversão e incerteza  
**Teste específico (NOT_RUN):** Evento duplicado e amostra insuficiente não geram conclusão causal  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-FIN-01 · Conciliação e fechamento

**Responsável:** NLE-PLUTUS-CFO | **Despacho:** NLE-PLUTUS-CFO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** Diário e mensal  
**Entradas:** Pedidos, faturas e extratos de leitura

### Etapas

1. **NLE-PLUTUS-CTRL (A2)**: conciliar receitas e custos. Skills elegíveis: financial-controllership.

2. **NLE-PLUTUS-TREAS (A2)**: projetar caixa. Skills elegíveis: corporate-finance.

3. **NLE-PLUTUS-CFO (A3)**: consolidar relatório. Skills elegíveis: corporate-finance.

**Entrega:** DRE gerencial, caixa e divergências  
**KPIs:** Diferenças abertas rastreadas; 0 lançamentos fictícios  
**Teste específico (NOT_RUN):** Estorno fora de ordem não duplica receita  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-FIN-02 · Orçamento e unit economics

**Responsável:** NLE-PLUTUS-CFO | **Despacho:** NLE-PLUTUS-CFO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Semanal ou proposta  
**Entradas:** Custos, metas e dados de receita

### Etapas

1. **NLE-PLUTUS-FPA (A2)**: modelar cenários. Skills elegíveis: financial-planning.

2. **NLE-PLUTUS-UNIT (A2)**: calcular margem, CAC e LTV. Skills elegíveis: core-unit-economics, financial-planning.

3. **NLE-PLUTUS-CFO (A3)**: propor alocação. Skills elegíveis: corporate-finance.

**Entrega:** Orçamento proposto e análise de margem  
**KPIs:** Gasto novo=0 por padrão; premissas rastreadas  
**Teste específico (NOT_RUN):** Orçamento insuficiente não libera ação paga  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-FIN-03 · FinOps, quotas e custos de IA

**Responsável:** NLE-PLUTUS-FINOPS | **Despacho:** NLE-PLUTUS-FINOPS | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** Por execução e diário  
**Entradas:** Telemetria e quotas verificadas

### Etapas

1. **NLE-PLUTUS-FINOPS (A3)**: reservar e reconciliar limites. Skills elegíveis: ai-finops, core-capacity-cost, core-tool-budget.

2. **NLE-ATLAS-AOPS (A3)**: aplicar backpressure. Skills elegíveis: core-incident-recovery, core-reliable-workflows, reliability-operations.

3. **NLE-ZEUS-CEO (A3)**: repriorizar fila. Skills elegíveis: core-capacity-cost, core-incident-recovery, executive-strategy.

**Entrega:** Ledger de recursos e alertas  
**KPIs:** 100% execuções com reserva; overspend=0  
**Teste específico (NOT_RUN):** Quota desconhecida ou exaurida impede fallback pago  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-FIN-04 · Compras e renovação

**Responsável:** NLE-ATLAS-COO | **Despacho:** NLE-ATLAS-COO | **Revisor:** NLE-PLUTUS-CFO | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Solicitação ou vencimento  
**Entradas:** Fornecedor, licença e custo

### Etapas

1. **NLE-ATLAS-PROC (A2)**: comparar alternativas. Skills elegíveis: procurement.

2. **NLE-PLUTUS-FPA (A2)**: avaliar impacto. Skills elegíveis: financial-planning.

3. **NLE-ARGUS-LEGAL (A1)**: analisar termos. Skills elegíveis: legal-research.

**Entrega:** Recomendação de compra sem compromisso  
**KPIs:** Custos evitados; renovações rastreadas  
**Teste específico (NOT_RUN):** Sem aceite humano não há contratação nem renovação  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-QNT-01 · Inteligência macro e sentimento

**Responsável:** NLE-POSEIDON-CIO | **Despacho:** NLE-ATHENA-PMO | **Revisor:** NLE-POSEIDON-RISK | **Risco:** STANDARD | **Gate:** INTERNAL_ONLY

**Gatilho:** Diário útil  
**Entradas:** Fontes públicas com timestamps

### Etapas

1. **NLE-POSEIDON-MACRO (A1)**: analisar releases. Skills elegíveis: macro-research.

2. **NLE-POSEIDON-SENT (A1)**: classificar notícias. Skills elegíveis: macro-research.

3. **NLE-POSEIDON-EQ (A1)**: avaliar fundamentos. Skills elegíveis: core-source-evidence, equity-research.

**Entrega:** Research datado, sem ordens  
**KPIs:** 100% dados com timestamp; hipóteses explícitas  
**Teste específico (NOT_RUN):** Notícia desatualizada ou não confirmada marcada como tal  
**Próximos candidatos condicionais:** NLE-WF-QNT-03

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-QNT-02 · Cripto e DeFi research

**Responsável:** NLE-POSEIDON-CIO | **Despacho:** NLE-ATHENA-PMO | **Revisor:** NLE-POSEIDON-RISK | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** Diário  
**Entradas:** Market data público e dados on-chain

### Etapas

1. **NLE-POSEIDON-CRYPTO (A1)**: analisar ativos. Skills elegíveis: crypto-research.

2. **NLE-POSEIDON-CHAIN (A1)**: validar métricas on-chain. Skills elegíveis: crypto-research.

3. **NLE-POSEIDON-DEFI (A1)**: avaliar riscos de protocolos. Skills elegíveis: crypto-research.

**Entrega:** Relatório de mercado sem carteira conectada  
**KPIs:** Fontes verificáveis; dados stale identificados  
**Teste específico (NOT_RUN):** Preço divergente ou RPC inválido bloqueia conclusão  
**Próximos candidatos condicionais:** NLE-WF-QNT-03

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-QNT-03 · Estratégia quantitativa e backtest

**Responsável:** NLE-POSEIDON-CIO | **Despacho:** NLE-ATHENA-PMO | **Revisor:** NLE-POSEIDON-RISK | **Risco:** HIGH_ASSURANCE | **Gate:** INTERNAL_ONLY

**Gatilho:** Hipótese aprovada  
**Entradas:** Dataset congelado e hipótese

### Etapas

1. **NLE-POSEIDON-QR (A2)**: definir hipótese e split temporal. Skills elegíveis: core-experiment-design, quantitative-research.

2. **NLE-POSEIDON-QD (A2)**: implementar backtest. Skills elegíveis: quantitative-research.

3. **NLE-POSEIDON-DERIV (A2)**: validar payoff e custos. Skills elegíveis: derivatives-research.

**Entrega:** Backtest reprodutível e relatório de riscos  
**KPIs:** Sem lookahead; custos e OOS presentes  
**Teste específico (NOT_RUN):** Leakage, survivorship bias ou slippage omitido bloqueiam  
**Próximos candidatos condicionais:** NLE-WF-QNT-04

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-QNT-04 · Paper trading cripto e forex

**Responsável:** NLE-ATLAS-COO | **Despacho:** NLE-ATLAS-COO | **Revisor:** NLE-POSEIDON-RISK | **Risco:** HIGH_ASSURANCE | **Gate:** INTERNAL_ONLY

**Gatilho:** Sessão simulada autorizada  
**Entradas:** Estratégia aprovada e feed público/mock

### Etapas

1. **NLE-POSEIDON-CT (A2)**: produzir sinais simulados. Skills elegíveis: crypto-paper-trading.

2. **NLE-POSEIDON-FX (A2)**: produzir sinais simulados. Skills elegíveis: forex-paper-trading.

3. **NLE-POSEIDON-TSE (A2)**: implementar fills e reconciliação fake. Skills elegíveis: core-reliable-workflows, trading-simulation-systems.

4. **NLE-ATLAS-AOPS (A3)**: operar somente runner simulado. Skills elegíveis: core-incident-recovery, core-reliable-workflows, reliability-operations.

**Entrega:** Ledger de ordens fictícias e PnL simulado  
**KPIs:** Drawdown, slippage e reconciliação; ordens reais=0  
**Teste específico (NOT_RUN):** Endpoint real, chave privada, stale feed ou perda de limite interrompem sessão  
**Próximos candidatos condicionais:** NLE-WF-QNT-05

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-QNT-05 · Validação de risco e relatório

**Responsável:** NLE-POSEIDON-CIO | **Despacho:** NLE-ATHENA-PMO | **Revisor:** NLE-ARGUS-ORA | **Risco:** HIGH_ASSURANCE | **Gate:** INTERNAL_ONLY

**Gatilho:** Fim da sessão ou backtest  
**Entradas:** Resultados e baseline

### Etapas

1. **NLE-POSEIDON-RISK (A2)**: calcular exposição e stress. Skills elegíveis: portfolio-risk.

2. **NLE-POSEIDON-CIO (A2)**: consolidar relatório de pesquisa. Skills elegíveis: core-risk-analysis, investment-research.

**Entrega:** Parecer de risco e evidências  
**KPIs:** 100% limites simulados avaliados; sem promessa de retorno  
**Teste específico (NOT_RUN):** Resultados negativos não são ocultados; sem promoção a live  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-OPS-01 · Onboarding e suporte

**Responsável:** NLE-ATLAS-COO | **Despacho:** NLE-ATLAS-COO | **Revisor:** NLE-ARGUS-PRIV | **Risco:** STANDARD | **Gate:** POLICY_GATED_EXTERNAL

**Gatilho:** Contrato ou ticket  
**Entradas:** Escopo, SLA e acessos mínimos

### Etapas

1. **NLE-ATLAS-IMP (A3)**: preparar onboarding. Skills elegíveis: core-incident-recovery, customer-implementation.

2. **NLE-ATLAS-SUP (A3)**: triar incidentes. Skills elegíveis: service-operations.

3. **NLE-ATLAS-CS (A3)**: acompanhar sucesso. Skills elegíveis: service-operations.

**Entrega:** Ticket, plano e aceite do cliente  
**KPIs:** Tempo de resposta, resolução e CSAT  
**Teste específico (NOT_RUN):** Cliente incorreto não recebe dados ou acesso  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-OPS-02 · Renovação e retenção

**Responsável:** NLE-ATLAS-COO | **Despacho:** NLE-ATLAS-COO | **Revisor:** NLE-ARGUS-LEGAL | **Risco:** STANDARD | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Sinal de churn ou vencimento  
**Entradas:** Uso, contrato e feedback

### Etapas

1. **NLE-ATLAS-CS (A3)**: identificar risco. Skills elegíveis: service-operations.

2. **NLE-HERMES-AE (A2)**: preparar proposta. Skills elegíveis: consultative-sales.

3. **NLE-PLUTUS-UNIT (A2)**: validar rentabilidade. Skills elegíveis: core-unit-economics, financial-planning.

**Entrega:** Plano de retenção sem compromisso  
**KPIs:** Churn, renovação e margem  
**Teste específico (NOT_RUN):** Renovação sem aceite não modifica contrato  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-OPS-03 · Observabilidade e recuperação

**Responsável:** NLE-ATLAS-COO | **Despacho:** NLE-ATLAS-COO | **Revisor:** NLE-ARGUS-CISO | **Risco:** ELEVATED | **Gate:** INTERNAL_ONLY

**Gatilho:** Alerta ou revisão diária  
**Entradas:** Health checks e backups

### Etapas

1. **NLE-ATLAS-AOPS (A3)**: monitorar filas. Skills elegíveis: core-incident-recovery, core-reliable-workflows, reliability-operations.

2. **NLE-HEPHAESTUS-SRE (A3)**: diagnosticar. Skills elegíveis: core-incident-recovery, reliability-operations.

3. **NLE-HEPHAESTUS-DEVOPS (A3)**: ensaiar restore. Skills elegíveis: core-incident-recovery, core-security-privacy, release-infrastructure.

4. **NLE-ATLAS-COO (A3)**: coordenar incidente. Skills elegíveis: core-capacity-cost, core-incident-recovery, service-operations.

**Entrega:** Incidente, evidência de recuperação e alerta  
**KPIs:** MTTR; RPO/RTO medidos; backups restauráveis  
**Teste específico (NOT_RUN):** Restore corrompido bloqueia retomada; produção exige autorização de mudança  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SEC-01 · Segurança contínua e resposta

**Responsável:** NLE-ARGUS-CISO | **Despacho:** NLE-ARGUS-CISO | **Revisor:** NLE-ARGUS-ORA | **Risco:** HIGH_ASSURANCE | **Gate:** INTERNAL_ONLY

**Gatilho:** Alerta, release ou revisão semanal  
**Entradas:** Logs e artefatos sanitizados

### Etapas

1. **NLE-ARGUS-APPSEC (A2)**: avaliar vulnerabilidades. Skills elegíveis: application-security, core-risk-analysis.

2. **NLE-ARGUS-AISEC (A2)**: testar agentes. Skills elegíveis: agent-security, core-security-privacy.

3. **NLE-ARGUS-PRIV (A2)**: avaliar exposição. Skills elegíveis: core-security-privacy, privacy-compliance.

4. **NLE-ARGUS-CISO (A3)**: propor contenção e bloquear fila. Skills elegíveis: core-incident-recovery, core-risk-analysis, core-security-privacy, security-governance.

**Entrega:** Registro de incidente e plano de correção  
**KPIs:** HIGH/CRITICAL abertos bloqueiam avanço  
**Teste específico (NOT_RUN):** Segredo exposto suspende execução; rotação real só por autoridade habilitada  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SEC-02 · Compliance e privacidade

**Responsável:** NLE-ARGUS-CISO | **Despacho:** NLE-ARGUS-CISO | **Revisor:** NLE-ARGUS-ORA | **Risco:** ELEVATED | **Gate:** HUMAN_APPROVAL_REQUIRED

**Gatilho:** Nova integração ou pedido de titular  
**Entradas:** Inventário de dados e políticas

### Etapas

1. **NLE-ARGUS-PRIV (A2)**: mapear finalidade, retenção e acesso. Skills elegíveis: core-security-privacy, privacy-compliance.

2. **NLE-ARGUS-LEGAL (A1)**: pesquisar requisitos. Skills elegíveis: legal-research.

3. **NLE-ATHENA-KM (A2)**: registrar fontes e política. Skills elegíveis: core-data-quality, core-source-evidence, knowledge-retrieval.

**Entrega:** Parecer e política proposta  
**KPIs:** 100% integrações com finalidade e escopo  
**Teste específico (NOT_RUN):** Pedido de exclusão não apaga registros sujeitos a retenção obrigatória sem revisão  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.



## NLE-WF-SEC-03 · Auditoria de permissões e gastos

**Responsável:** NLE-ARGUS-CISO | **Despacho:** NLE-ARGUS-CISO | **Revisor:** NLE-ARGUS-SWA | **Risco:** HIGH_ASSURANCE | **Gate:** INTERNAL_ONLY

**Gatilho:** Diário e mudança de grants  
**Entradas:** Eventos de auditoria, locks e autorizações

### Etapas

1. **NLE-ARGUS-ORA (A2)**: detectar segregação violada. Skills elegíveis: core-incident-recovery, core-risk-analysis, security-governance.

2. **NLE-ARGUS-AISEC (A2)**: validar tool gateway. Skills elegíveis: agent-security, core-security-privacy.

3. **NLE-PLUTUS-FINOPS (A3)**: reconciliar uso. Skills elegíveis: ai-finops, core-capacity-cost, core-tool-budget.

**Entrega:** Relatório de violações e bloqueios  
**KPIs:** Aprovação própria=0; gasto indevido=0  
**Teste específico (NOT_RUN):** Grant vencido, escopo divergente ou autoaprovação são negados  
**Próximos candidatos condicionais:** encerrar/aguardar próximo evento

**Falhas:** BLOCKED on missing gate, ambiguous external effect or critical defect; internal retry only if idempotent; route correction to same run; escalate to accountable/ARGUS and owner as needed.


