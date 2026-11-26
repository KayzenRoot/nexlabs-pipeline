# Provenance | NLE-BOOTSTRAP-001/CD-03

Este documento separa duas cadeias de evidência que **não** devem ser confundidas:

1. **Proveniência do pacote original** — prova de que os bytes vieram do Source Pack entregue e conferem com o `source-lock`.
2. **Estado Git remoto** — prova do ponto de revisão, da CI, da governança e da auditoria no repositório.

Nenhuma das duas, isoladamente, prova runtime, aprovação humana, deploy ou custo zero. A aprovação depende de auditoria independente e dos gates do Work Order.

## 1. Proveniência do pacote original (imutável)

| Item | Valor |
|---|---|
| Arquivo | `NLE-BOOTSTRAP-001_NexLabs_Pipeline.zip` |
| Tamanho | 1.557.156 bytes |
| SHA-256 | `1c012736772aba8a96bc27f796194d4a77f1f88a7ff66ee37c2512f2d6129844` |
| Entradas | 394 |
| Conteúdo extraído | 4.264.032 bytes |
| Integridade | `testzip()` OK; 0 caminhos inseguros; 0 symlinks |
| Source lock | `locks/source-lock.json`, SHA-256 `a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e` |
| Originais | 364 arquivos, 6 ZIPs; 364/364 hashes SHA-256 conferem; 0 ausentes, 0 divergentes, 0 extras |
| Subconjunto já versionado | 325 arquivos; todos os blobs Git conferem com o lock; 39 adicionados |
| Árvore Git do subconjunto | `3856ba9b4995443510166cefa5f2550394465be5` |

**Nota de proveniência:** o campo `status` do `source-lock` (`LOCAL_SNAPSHOT_BLOCKED_PUBLIC_REPO`) e `git_base: null` são metadados históricos do snapshot original, não o estado atual do Git remoto. O lock é âncora de proveniência e não deve ser reescrito sem recalcular todos os ponteiros; o estado atual está na seção 2.

O pacote original foi produzido na fase CD-01 (documentos com referência histórica a alvo privado). A exceção pública temporária é regida por **NLE-ADR-BOOT-007**, preservada no Decisions Ledger. Os bytes de `sources/` não foram alterados; documentos candidatos foram reconciliados com o histórico CD-01/CD-02.

## 2. Estado Git remoto (mutável)

| Item | Valor |
|---|---|
| Repositório | `KayzenRoot/nexlabs-pipeline`, ID `1472951510` |
| Visibilidade | PUBLIC, sob NLE-ADR-BOOT-007 (produção privada) |
| Base | `48d3e422313f869992d09b99f0b7e09acd4e1caa` |
| Branch | `chore/nle-bootstrap-001` |
| PR | #1, merged/closed via squash |
| HEAD no início do CD-03 | `70418070aa80b2b35093be46e87fb246eacfeb6a` |
| HEAD auditado | `668a77eb5683254018476cdeb02dcfdfcbbc6ca6` |
| HEAD final auditado Round 2 | `a1c7eee9b3cb37ed3a2f778facd17b6355ff90a0` |
| CI final | run `45829492379`, success no HEAD `a1c7eee9b3cb37ed3a2f778facd17b6355ff90a0`; GitHub Actions, runner padrão `ubuntu-24.04` |
| Check obrigatório | `docs-validation`, app_id `15368`, `strict=true`, lido de volta |
| Auditoria independente | Round 1 CORRECTION REQUIRED corrigido; Round 2 **APPROVED** por agente independente read-only; comentário final https://github.com/KayzenRoot/nexlabs-pipeline/pull/1#issuecomment-7193611818 |

| Squash merge | `301905ac0f9eb6ddeb2338c9caa74a8516858a50`; `main` read-back no mesmo SHA |
| Custo | US$0 adicional qualificado por política pública + runner padrão; billing API não lida (UNVERIFIED) |

## 3. Regra de leitura

- O SHA-256 do ZIP e o `source-lock` provam **proveniência** dos originais.
- O SHA Git do HEAD auditado prova o **ponto exato** revisado.
- O run de CI prova **execução** do validador e dos 7 testes naquele ponto.
- O read-back de proteção/ruleset prova **governança**.
- A auditoria independente prova **revisão separada**; ela não é autoaprovação.
- Merge da PR #1 foi autorizado pelo proprietário e concluído via squash em `301905ac0f9eb6ddeb2338c9caa74a8516858a50`.
- Nenhuma evidência autoriza deploy, gasto, agentes, skills, rotinas ou integrações externas.
