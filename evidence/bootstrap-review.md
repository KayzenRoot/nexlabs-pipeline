# Local Evidence Bundle | NLE-BOOTSTRAP-001
Estado: LOCAL_SOURCE_PACK_CANDIDATE / BLOCKED_REMOTE. Auditoria independente não executada. Base/head Git: N/A; PR: N/A; CI: NOT_RUN. Fonte remota consultada: NexLabsTech/nexlabs-enterprise via conexão da organização, HTTP 404. Não houve escrita remota.

| AC | Resultado local | Evidência |
|---|---|---|
| AC01 | BLOCKED | 404; identidade de conexão usada, acesso/visibilidade/base desconhecidos |
| AC02 | PASS local | 6 ZIPs, 364 fontes SHA256, byte equality; 105/92/1110/62/35, 1071 registros, 316 cenários |
| AC03 | PASS estrutural com ressalva C12 | Validador confirma limites, vínculos e cinco discrepâncias dispatch-only; correção de contrato requerida antes de runtime, nenhuma permissão promovida |
| AC04 | PASS local | Source Pack, backlog 40 IDs únicos e predecessor sequencial; dependências a revalidar em cada WO |
| AC05 | PASS documental | Decisions Ledger, índice e Consistency Audit; decisões de bootstrap propostas |
| AC06 | BLOCKED | Context Lock template sem SHA; validação local PASS, CI não executado |
| AC07 | BLOCKED | Ruleset, settings e quotas não verificados; nenhuma nova despesa realizada |
| AC08 | BLOCKED | Evidência local e prompt gerados; PR remota pendente |
| AC09 | NOT_RUN | Aprovação independente, promoção e merge pendentes |

Comandos: `python scripts/validate_sources.py`; `python -m unittest discover -s tests -v`. Resultado: 7/7 testes (1 positivo e 6 negativos de integridade/backlog) e 7 grupos de verificações do validador PASS, com C12 explicitamente detectado. O primeiro teste mais estrito encontrou divergência entre participantes e matriz; ajustado o validador para reconhecer a distinção de despachante sem conceder permissões e exigir o conjunto exato de exceções. Não se corrigiu o contrato de runtime neste WO. Não houve lint/typecheck/build de aplicativo (N/A, sem aplicativo), testes operacionais ou benchmark real. O SHA256 dos artefatos protege integridade local, não substitui Git Context Lock.

Checkpoint Delta proposto: manter NLE-BOOTSTRAP-001 em andamento/BLOCKED_REMOTE; registrar ratificações de direção e C12; somente após AC01–AC09 satisfeitos e auditoria independente promover e iniciar NLE-INFRA-WO-001 read-only. Nenhum deploy, skill, rotina, cliente, operação externa ou financeira habilitada. Riscos restantes em docs/Consistency-Audit.md.

## Delta CD-01 (novo destino)
AC01: acesso admin/push comprovado no novo alvo, mas BLOCKED_PUBLIC_REPO; falta visibilidade PRIVATE e base. AC06–AC09 continuam pendentes. C01 atualizado, C02–C12 preservados. O estado 404 acima é histórico. Nenhum push/PR executado. Checkpoint Delta proposto: manter NLE-BOOTSTRAP-001 bloqueado até read-back de privacidade e demais gates.
