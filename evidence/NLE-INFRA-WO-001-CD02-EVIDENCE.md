# Evidence Bundle | NLE-INFRA-WO-001/CD-02 — LOCAL FIRST

Status: **LOCAL_RUNTIME_HEALTHY_PENDING_OWNER_CLAIM_AND_CODEX_AUTH**
Data: 2026-11-26
Repositório: `KayzenRoot/nexlabs-pipeline`
Branch: `work/nle-infra-wo-001`
PR: #3 — https://github.com/KayzenRoot/nexlabs-pipeline/pull/3
Base: `8321110a2ff29aec90ffc1c384ea21f722de0497`
Head no início da execução: `7e3fd8f71fb283274301cfdab714826c046f2917`
Head final: registrado no comentário da PR #3 após o push, sem hash autorreferente.
Decisão: **NLE-ADR-INFRA-011 — LOCAL FIRST**.

## 1. Resumo

A estratégia LOCAL FIRST foi registrada; o Context Lock CD-01 anterior foi marcado STALE e um novo Context Lock CD-02 foi gerado. A estrutura portátil de deployment, a imagem oficial pinada por digest multi-arquitetura, os scripts PowerShell, os testes de contrato e a documentação operacional foram implementados. Os testes estáticos/offline e o Source Pack passaram.

Após autorização explícita do proprietário, **Docker Desktop 4.100.1** foi instalado do instalador oficial (SHA-256 verificado), o engine 29.9.3 iniciou e o **Paperclip está rodando healthy** em `127.0.0.1:3100`, com health 200, UI 200, persistência/restart, backup e restauração isolada validados. O navegador foi aberto para o claim da instância; nenhuma conta foi criada. Claim do proprietário e autenticação Codex por assinatura permanecem pendentes. Nenhum agente, workflow, heartbeat, API key, deploy VPS, gasto ou efeito externo foi ativado.

## 2. Source Check e host

| Item | Resultado |
|---|---|
| Repositório/PR | `KayzenRoot/nexlabs-pipeline`, PR #3 draft, branch `work/nle-infra-wo-001` |
| Base | `8321110a2ff29aec90ffc1c384ea21f722de0497` |
| Windows | Windows 11 Home Single Language 10.0.26200, build 26200, x64 |
| CPU | 8 processadores lógicos |
| RAM | 24.591.810.560 bytes |
| Virtualização | firmware habilitado |
| WSL2 | Ubuntu-26.04, versão 2, estado Stopped |
| Docker Desktop | **4.100.1 instalado**; instalador oficial SHA-256 `98b24fd6…39b2` |
| Docker engine | **29.9.3**; WSL2 backend |
| Porta 3100 | **127.0.0.1:3100**, container healthy |
| Disco | C: 29,96 GiB livres; D: 119,87 GiB livres |

## 3. Contratos oficiais do Paperclip

- Repositório oficial: https://github.com/paperclipai/paperclip
- Release: `v2026.1117.0` (imagem usa o tag `2026.1117.0`)
- Índice imutável: `sha256:bdf38d10544dc6c831e16dc027f23ad586353ef3be1a1b2c6979e63b956aceb1`
- `linux/amd64`: `sha256:b2784df63b428a3de231039f03c2a78f582dcf5e35e840685685c8cef28814e2`
- `linux/arm64`: `sha256:84b21aae73c14d482039868c784c2146cfd6d5e2efcc1d86b7e51c60bf0e4134`
- Variante Cloud: **não usada**.
- Banco: PostgreSQL incorporado quando `DATABASE_URL` não é definido; PostgreSQL externo quando definido.
- Health: `/api/health`.
- Codex: imagem oficial inclui Codex CLI e adapter `codex_local`; autenticação por assinatura, sem API key.

PostgreSQL externo futuro: `postgres:17-alpine` no índice `sha256:f9cf3e1f0066f0eb0c48707d864f0ac5941e9ff454a072077d97a4d278d07d73`, com manifests `linux/amd64` e `linux/arm64`.

## 4. Implementação

- `deploy/compose.yaml` — base portátil, imagem pinada, healthcheck `/api/health`, secrets obrigatórios, sem portas públicas.
- `deploy/local/compose.yaml` — override Windows com bind `127.0.0.1:3100` e volume persistente.
- `deploy/vps/compose.yaml` — preparação futura com PostgreSQL 17 externo pinado, `DATABASE_URL`, sem porta pública e sem execução neste WO.
- `deploy/image-lock.json` — tag, índice e manifests por arquitetura.
- `deploy/README.md`, `deploy/local/README.md`, `deploy/vps/README.md`, `deploy/local/codex/README.md`, `deploy/local/agents/README.md` — documentação operacional e limites.
- `scripts/windows/Paperclip.Common.ps1` — funções compartilhadas, secrets, ACL, compose, health, backup/restore.
- `scripts/windows/Initialize-PaperclipSecrets.ps1` — criação única dos dois segredos.
- `scripts/windows/Start-Paperclip.ps1` — fail-closed, valida Docker/secrets/porta, inicia compose e aguarda health.
- `scripts/windows/Stop-Paperclip.ps1` — `docker compose stop` graceful; sem remoção de volumes.
- `scripts/windows/Get-PaperclipStatus.ps1` — status e health.
- `scripts/windows/Backup-Paperclip.ps1` — parada segura, arquivo completo do data dir, SHA-256, reinício.
- `scripts/windows/Restore-Paperclip.ps1` — verificação de integridade e restauração em diretório isolado.
- `scripts/windows/Test-PaperclipDeployment.ps1` — self-test offline.
- `tests/deployment/test_deploy_contract.py` — contratos estáticos stdlib.
- `docs/Checkpoint.md`, `docs/Decisions-Ledger.md`, `docs/Backlog.md`, `docs/Architecture.md`, `docs/Deployment.md` e `docs/decisions-index.json` — decisão, escopo e delta registrados.
- `locks/NLE-INFRA-WO-001-context-lock.json` — novo lock; `locks/history/NLE-INFRA-WO-001-context-lock-CD01.json` — lock anterior STALE.

## 5. Segurança

- Segredos `BETTER_AUTH_SECRET` e `PAPERCLIP_TOOL_ACTION_SIGNING_SECRET` gerados com CSPRNG de 32 bytes cada, em `D:\NexLabs\Paperclip\secrets\paperclip.env`.
- Arquivo com 2 linhas, 186 bytes, ACL protegida (`AreAccessRulesProtected=True`), somente o usuário atual com FullControl.
- Valores **não foram impressos, logados ou versionados**.
- `.gitignore` cobre `deploy/**/data/`, `backups/`, `restore-test-*`, `secrets/`, `paperclip.env`, arquivos compactados e chaves.
- Varredura de 435 arquivos versionados/não rastreados: 0 chaves privadas, tokens, credenciais em URL, e-mails, CPF/CNPJ ou valores de secret.
- Sem API keys, sem Cloud image, sem agentes, sem heartbeats/workflows/efeitos externos, sem VPS/SSH/deploy.

## 6. Testes reais

| Teste | Resultado |
|---|---|
| `python scripts/validate_sources.py` | 7 grupos PASS; exit 0 |
| `python -m unittest discover -s tests -v` | 26/26 OK; exit 0 |
| `Test-PaperclipDeployment.ps1` offline | 30/30 PASS; exit 0 |
| Restore com sidecar ausente | FAIL-CLOSED `BACKUP_SIDECAR_MISSING` |
| Parse YAML dos 3 Compose | PASS; services `paperclip`, `paperclip`, `db+paperclip` |
| Docker Desktop | **4.100.1 instalado**; engine **29.9.3** |
| Container | `nexlabs-paperclip-paperclip-1` **healthy**; `127.0.0.1:3100->3100/tcp` |
| `/api/health` | **200**; status ok; deploymentMode authenticated; exposure private; bootstrap_pending |
| UI `http://localhost:3100/` | **200** |
| Persistência stop/start | PASS; 3.540 arquivos / ~89 MB; health 200 após restart |
| Backup | `paperclip-data-20261126T180447Z.zip`, 12,96 MiB, SHA-256 `b1dea3e66ee2f523de672bd750be546301aa8673529798e2730bc1e3ebbb8106` |
| Restore isolado | PASS; permissões `0700` reparadas; instância restaurada **healthy 200** na porta 3101 |
| Exposição | somente `127.0.0.1:3100` |
| Owner claim / Codex | navegador aberto; `bootstrap_pending`; claim e autenticação por assinatura pendentes |
| GitHub Actions | run `45845361323` success em `6a7aaa2` (auditado) e run `45848372035` success em `8f6af9e`; `docs-validation`, labels `["ubuntu-24.04"]`, 26/26 testes |
| `git diff --check` | Limpo no diff do CD-02 e no range completo após remover whitespace histórico do WO |
| Source Pack | 364/364 + 6 ZIPs; 105/92/1110/1071/62/35 preservados |

## 7. AC01–AC19

Os AC01–AC09 originais do CD-01 são preservados como histórico read-only. O CD-02 adiciona:

| AC | Status | Evidência |
|---|---|---|
| AC10 decisão/backlog/WO/lock | **PASS** | NLE-ADR-INFRA-011, Backlog, WO CD-02, lock novo e lock antigo STALE |
| AC11 Compose portátil e imagem pinada | **PASS** | índice `bdf38d…`, amd64/arm64 verificados, sem `latest` |
| AC12 local loopback/persistência/health | **PASS estático** | `127.0.0.1:3100`, volume, `/api/health` |
| AC13 segredos fora do Git/protegidos | **PASS** | 2 secrets, ACL protegida, valores não registrados |
| AC14 scripts e segurança offline | **PASS** | 30/30 self-test; restore fail-closed; sem `down -v`, prune ou force-recreate |
| AC15 runtime start/health/persistência/restart/backup | **PASS** | Paperclip healthy; health 200; persistência/restart; backup e restore isolado validados |
| AC16 Codex preparado | **PASS parcial** | `codex_local`/assinatura preparado; sem API key/cópia de auth; autenticação pendente do proprietário |
| AC17 VPS preparada | **PASS documental** | Compose externo PostgreSQL/ARM64; sem SSH/deploy |
| AC18 catálogo preservado | **PASS** | 105/92/1110/1071/62/35; sem importação/ativação |
| AC19 testes/CI/auditoria/evidência | **PASS*** | 7 PASS + 26/26 CI + 30/30 offline; auditoria independente APPROVED na implementação; runtime validado pelo executor; auditoria de runtime pendente |

## 7.1 Auditoria independente

Auditoria read-only por agente separado no HEAD `6a7aaa2`:

- **Implementação: APPROVED**, com achados LOW não bloqueantes.
- **Runtime na auditoria: BLOCKED** — Docker Desktop/CLI estava ausente naquele momento. Após autorização do proprietário, Docker Desktop 4.100.1 foi instalado e o runtime foi validado pelo executor; auditoria independente de runtime ainda pendente.
- Sem achados CRITICAL/HIGH/MEDIUM.
- LOW-1 trailing whitespace: corrigido no WO; range completo limpo após o commit corretivo.
- LOW-2 Context Lock não ancorado ao HEAD final/CI: corrigido com `head_audited`, `head_after_implementation`, CI `45845361323` e run de testes.
- LOW-3 restore fail-open sem sidecar: corrigido para `BACKUP_SIDECAR_MISSING`; self-test cobre.
- LOW-4 ACL/.gitignore: ACL agora purga ACEs não-owner via `icacls /reset`; `.gitignore` cobre `paperclip.env`, `paperclip-data/`, `restore-test-*` e backups em qualquer raiz.
- Jev 1.14.0: 6/6 claims verificadas.
- A auditoria é de agente, **não é aprovação humana**; merge/promoção seguem não autorizados.

## 8. Runtime validado e pendências

- Docker Desktop **4.100.1** instalado do instalador oficial (SHA-256 `98b24fd6f56313899953ca4d2ed05645d69963b598143b75c6585fa4f7f639b2`); engine **29.9.3**.
- Container `nexlabs-paperclip-paperclip-1` **healthy**; `/api/health` **200**; UI **200**; porta somente `127.0.0.1:3100`.
- Persistência stop/start: 3.540 arquivos/~89 MB; health 200 após restart.
- Backup completo: 12,96 MiB; SHA-256 `b1dea3e66ee2f523de672bd750be546301aa8673529798e2730bc1e3ebbb8106`.
- Restore isolado: permissões `0700` reparadas; instância restaurada **healthy 200** na porta 3101; container temporário removido.
- Navegador aberto em `http://localhost:3100`; `bootstrap_pending`; nenhuma conta criada. **Claim do proprietário e autenticação Codex por assinatura pendentes.**
- Docker Desktop foi instalado com `--accept-license` por instrução explícita do proprietário; nenhuma conta, assinatura ou cobrança Docker foi criada. Licenciamento comercial deve ser confirmado pelo proprietário.
- Nenhum acesso à VPS, SSH, firewall/NSG/DNS, deploy remoto, agente, workflow, heartbeat, API key ou gasto.

## 9. Checkpoint Delta proposto

**`LOCAL_RUNTIME_HEALTHY_PENDING_OWNER_CLAIM_AND_CODEX_AUTH`**

- Implementação aprovada; runtime local healthy; persistência/backup/restore validados.
- Claim do proprietário e Codex por assinatura pendentes.
- Nenhuma promoção de checkpoint, merge ou avanço para NLE-SR-WO-001.
- Próximo WO após autorização do proprietário: **NLE-SR-WO-001** (registry schema, locks, quarentena e validador). Não iniciar.

## 10. Veredito

**LOCAL_RUNTIME_HEALTHY** — implementação **APPROVED** pela auditoria independente e runtime local validado pelo executor. Paperclip está rodando em `127.0.0.1:3100`, com health 200, persistência, backup e restore isolado comprovados. Claim da instância e autenticação Codex por assinatura permanecem pendentes de ação do proprietário. Não é aprovação humana, não é merge e não conclui a NexLabs AI Enterprise v1.0.
