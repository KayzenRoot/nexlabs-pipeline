# corporate-finance

Status: SPECIFIED_NOT_QUALIFIED | Version: 0.1.0-proposed | Risk: HIGH_ASSURANCE

## Contrato
- Gatilho: tarefa autorizada que exige corporate finance; não usar fora da responsabilidade do agente.
- Entradas: objetivo, escopo, contexto de domínio, fontes com versão, restrições e fixture.
- Saída esperada: Fluxo de caixa e política de despesa.
- Procedimento: validar Context Lock e fontes; selecionar competência pertinente; aplicar método documentado e ferramentas permitidas; verificar resultados por teste/contraprova; registrar evidência, limitações e handoff.
- Parar: fonte insuficiente, orçamento/permite negado, contexto STALE, falha de teste ou ação externa sem aprovação.
- Ferramentas: nenhuma concedida por este pacote; derivar allowlist por agente e tarefa no preflight.
- Fontes candidatas: OWN; sem importação automática.

## Competências rastreadas (20)
- aging
- calendário financeiro
- capital allocation
- capital de giro
- cash flow
- cenários
- cenários de stress
- conciliação bancária
- contas a pagar
- contas a receber
- controle de margem
- DRE
- FinOps
- gestão de caixa
- governança de despesas
- liquidez
- orçamento
- planejamento financeiro
- projeção de caixa
- risco financeiro

## Avaliação
- Cenário de pacote: Reconciliação e bloqueio de pagamento não autorizado.
- Provas: fixture versionada, saída estruturada, asserção verificável, logs redigidos, SHA do pacote/modelo/adapter; cenário negativo obrigatório.
- Testes individuais herdados: NLE-PLUTUS-CFO-Q01, NLE-PLUTUS-CFO-Q02, NLE-PLUTUS-CFO-Q03, NLE-PLUTUS-TREAS-Q01, NLE-PLUTUS-TREAS-Q02, NLE-PLUTUS-TREAS-Q03.
- Aceite: gates SR01–SR06; pontuação >=90/100 e zero falha crítica; revisão independente (auditores não se autoaprovam).
- Estado: NOT_RUN. Implementar método e fixture específicos antes de criar SKILL.md.

