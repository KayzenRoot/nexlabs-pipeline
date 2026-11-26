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

## Delta LOCAL FIRST | NLE-INFRA-WO-001/CD-02
| ID | Estado | Decisão / restrição |
|---|---|---|
| NLE-ADR-INFRA-011 | RATIFIED_DIRECTION | O proprietário aprova LOCAL FIRST: instalar e validar Paperclip neste Windows 11 antes de qualquer implantação na VPS Oracle. Docker Desktop com backend WSL2, containers Linux, imagem oficial pinada por digest, acesso somente `127.0.0.1:3100`, PostgreSQL incorporado com persistência, configuração preparada para PostgreSQL externo e ARM64 na VPS futura. Sem acesso/SSH/deploy na VPS, sem API keys, sem agentes, sem heartbeats/workflows/efeitos externos e sem gasto. |

NLE-ADR-INFRA-011 é uma mudança de estratégia explicitamente autorizada pelo proprietário. Ela supersede **somente** a proibição de instalação local contida no NLE-INFRA-WO-001/CD-01 read-only; o inventário read-only permanece preservado como subescopo histórico. A implantação na VPS, o acesso remoto, a qualificação de runtime e a ativação de agentes continuam fora de escopo. Nenhuma decisão anterior é apagada ou reinterpretada além deste delta.

## Estado integrado | NLE-INFRA-WO-001/CD-03 — 2026-11-26
- **APPROVED / SQUASH_MERGED / CHECKPOINT PROMOTED após integração deste delta documental.** PR #3 merged; HEAD aprovado `14d258a13503cf29dca9baeb31a5b5ada2d500ac`; squash/read-back `28a40b0f6ddf3b4dee5f2663ec96639a74cc49fd`; árvore do merge idêntica ao HEAD aprovado (`d917d854b4962ccdb0894318d4ad41a362876e7c`). CI final 45893169254 success; 364/364 originais inalterados; 44 fingerprints Git conferidos; SHA-256 44/44 reportados pelo auditor local. Auditoria independente: https://github.com/KayzenRoot/nexlabs-pipeline/pull/3#issuecomment-7203032835; HEAD de auditoria 51dbfeb, delta final exclusivamente documental, conferido no GitHub.
- LOCAL FIRST (NLE-ADR-INFRA-011): instalação Windows 11 healthy, loopback, claim e AC16 PASS por conexão gerenciada de assinatura. Validador 7 grupos PASS, Python 34/34, PowerShell 43/43 reportados; SonarCloud 0 novas issues e ECC Security Evidence passou por comentário (publicação de check indisponível). Docker elegibilidade gratuita atestada; billing API não consultada. Nenhum acesso VPS, compra ou execução de agente.
- Riscos residuais: backup pré-auth não prova recuperação da conexão atual; novo backup frio protegido obrigatório antes de depender de recuperação autenticada. Conexão compartilhada exige grants mínimos antes de qualquer ativação; Zeus default pausado (zero tarefas); reconciliar com identidade canônica, não duplicar. C12 permanece gate HIGH de runtime. Repositório público temporário; sem credenciais/dados privados nos novos arquivos; não autoriza produção.
- Próximo NECESSARY: NLE-SR-WO-001, schema/locks/quarentena/validator e provisionador offline dry-run, sem gravação em Paperclip ou chamadas de modelo. Somente após integração/read-back deste delta.
