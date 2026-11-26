# Decisions Ledger
Fonte de ratificação: mensagens explícitas do proprietário nesta conversa. Não equivalem a commit Git ou prova de implementação. Estados: RATIFIED_DIRECTION, PROPOSED, APPROVED (apenas após auditoria/promoção Git), BLOCKED, SUPERSEDED.
| ID | Estado | Decisão / restrição |
|---|---|---|
| NLE-INT-PLAN-001 | RATIFIED_DIRECTION | Seis memórias, RAG híbrido, grafo relacional, learning controlado; INT-ADR-001..008 preservados |
| NLE-INFRA-PLAN-001 | RATIFIED_DIRECTION | Oracle ARM64 + Windows, WireGuard, PostgreSQL, quotas e Codex direto; INFRA-ADR-001..010 preservados |
| NLE-CC-PLAN-001 | RATIFIED_DIRECTION | 35 superfícies, reutilizar Paperclip; CC-ADR-001..007 preservados, integração condicionada |
| CC-ADR-003 | RATIFIED_DIRECTION | Design Obsidian / Neon Glass, responsivo e acessível |
| NLE-BASELINE-001 | PROPOSED | Catálogo 105/92/1110/62/35 preservado a pedido explícito; não ratificar licenças ou execução |
| ADR-SR-001..005 | PROPOSED | Preservar conteúdo do Skills Registry; Git, locks, quarentena, permissões, releases |
| WF-ADR-001..005 | PROPOSED | Preservar conteúdo dos workflows; efeitos deny, evento/ledger, segregação |
| NLE-ADR-BOOT-001 | PROPOSED | Snapshots imutáveis e fingerprints; documentos canônicos prevalecem após auditoria |
| NLE-ADR-BOOT-002 | PROPOSED | Backlog sequencial único de 40 WOs de domínio, sem nova camada de execução concorrente |
| NLE-ADR-BOOT-003 | PROPOSED | Plugin vs sidecar decidido em CC-WO-001 via PoC pinada e autorização; sem fork inicial |
| NLE-ADR-BOOT-004 | PROPOSED | Segurança e US$0 são gates fail-closed; não duplicar controles nativos |
| NLE-ADR-BOOT-005 | PROPOSED | Planejamento não concede execução, acesso externo, gasto ou promoção de skill |
Não alterar snapshots de ADRs. Índice individual em decisions-index.json; o plano ratificado estabelece direção, parâmetros candidatos continuam condicionados. SR/WF são fontes solicitadas, sem ratificação explícita anterior comprovada de todos ADRs. Auditoria bootstrap deve validar e pedir resolução das decisões propostas que bloqueiem o próximo WO. Nenhuma ADR prévia sobrescrita.

## Delta de destino | NLE-BOOTSTRAP-001/CD-01 (histórico)
NLE-ADR-BOOT-006 — RATIFIED_DIRECTION: o proprietário indicou `nexlabs-pipeline`; Source Check autenticado identifica `KayzenRoot/nexlabs-pipeline`. Substitui apenas o destino histórico `NexLabsTech/nexlabs-enterprise`. A exigência de repositório privado permanece (posteriormente limitada por NLE-ADR-BOOT-007 **somente** para desenvolvimento revisado e não sensível; produção privada). Integração e implementação não aprovadas; sem criação de outro repo.

## Delta de visibilidade | NLE-BOOTSTRAP-001/CD-02
| ID | Estado | Decisão / restrição |
|---|---|---|
| NLE-ADR-BOOT-007 | RATIFIED_DIRECTION | O proprietário autoriza repositório público temporário para planejamento/desenvolvimento revisado e não sensível, substituindo o gate private-only durante esta fase; produção privada permanece. Sem dados de clientes, segredos ou credenciais no Git. Sem aprovação de deploy ou gasto. |

NLE-ADR-BOOT-007 é um delta estreito e explicitamente autorizado pelo proprietário. Ele supersede a exigência de repositório privado do CD-01 **somente** para material revisado e não sensível durante o bootstrap; não autoriza produção pública, dados reais, segredos, deploy, gasto ou ativação de agentes. NLE-ADR-BOOT-006 e todas as decisões anteriores permanecem preservadas. A conversão futura para privado não apaga cópias públicas anteriores. Nenhuma aprovação de implementação é inferida.


## Registro de execução | NLE-BOOTSTRAP-001/CD-04 (não é nova ADR)
Em 2026-11-26, após Round 2 independente APPROVED e autorização explícita do proprietário, PR #1 foi squash-merged. HEAD aprovado `a1c7eee9b3cb37ed3a2f778facd17b6355ff90a0`; merge commit e read-back da `main`: `301905ac0f9eb6ddeb2338c9caa74a8516858a50`. O checkpoint foi promovido sem alterar decisões de arquitetura. Riscos residuais: repositório público temporário (NLE-ADR-BOOT-007), billing API UNVERIFIED, GitHub approving review count=0, runtime não qualificado e C12 aberto. Nenhuma despesa, deploy ou ativação autorizada. NLE-INFRA-WO-001 não iniciado.
