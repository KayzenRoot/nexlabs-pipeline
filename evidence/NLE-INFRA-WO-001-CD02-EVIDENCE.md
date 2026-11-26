# Evidence Bundle | NLE-INFRA-WO-001/CD-02 — LOCAL FIRST

Status: **IMPLEMENTATION_PREPARED_RUNTIME_BLOCKED_DOCKER_ABSENT**
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

O Paperclip **não foi iniciado** porque **Docker Desktop não está instalado** e o CLI/daemon Docker não existe neste host. A instalação de Docker Desktop ou a habilitação de recursos do Windows exigiria ação administrativa não autorizada. O runtime permanece **BLOCKED**, conforme a stop condition do Work Order. Nenhum agente, workflow, heartbeat, API key, deploy, VPS, gasto ou efeito externo foi ativado.

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
| Docker Desktop | **AUSENTE** (`Docker Desktop.exe` não existe) |
| Docker CLI/daemon | **AUSENTE** (`docker` retorna 127) |
| Porta 3100 | **LIVRE** (sem listener) |
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
| `Test-PaperclipDeployment.ps1` offline | 29/29 PASS; exit 0 |
| Parse YAML dos 3 Compose | PASS; services `paperclip`, `paperclip`, `db+paperclip` |
| `docker version` | BLOCKED — comando ausente, exit 127 |
| `docker compose version` | BLOCKED — comando ausente, exit 127 |
| `Start-Paperclip.ps1` | FAIL-CLOSED `DOCKER_CLI_MISSING`, exit 2 |
| `Stop-Paperclip.ps1` | FAIL-CLOSED `DOCKER_CLI_MISSING`, exit 2 |
| `Get-PaperclipStatus.ps1` | `DOCKER_UNAVAILABLE`, exit 2 |
| Porta 3100 | LIVRE |
| Backup/restore offline | PASS, incluindo sentinelas e detecção de tamper |
| Exposição | Configuração estática `127.0.0.1:3100`; runtime não executado |
| `git diff --check` | Limpo |
| Source Pack | 364/364 + 6 ZIPs; 105/92/1110/1071/62/35 preservados |

## 7. AC01–AC19

Os AC01–AC09 originais do CD-01 são preservados como histórico read-only. O CD-02 adiciona:

| AC | Status | Evidência |
|---|---|---|
| AC10 decisão/backlog/WO/lock | **PASS** | NLE-ADR-INFRA-011, Backlog, WO CD-02, lock novo e lock antigo STALE |
| AC11 Compose portátil e imagem pinada | **PASS** | índice `bdf38d…`, amd64/arm64 verificados, sem `latest` |
| AC12 local loopback/persistência/health | **PASS estático** | `127.0.0.1:3100`, volume, `/api/health` |
| AC13 segredos fora do Git/protegidos | **PASS** | 2 secrets, ACL protegida, valores não registrados |
| AC14 scripts e segurança offline | **PASS** | 29/29 self-test; sem `down -v`, prune ou force-recreate |
| AC15 runtime start/health/persistência/restart/backup | **BLOCKED_DOCKER_ABSENT** | Docker Desktop/CLI ausente; nenhuma instalação administrativa executada |
| AC16 Codex preparado | **PASS documental** | `codex_local`, assinatura, sem API key, sem cópia de auth |
| AC17 VPS preparada | **PASS documental** | Compose externo PostgreSQL/ARM64; sem SSH/deploy |
| AC18 catálogo preservado | **PASS** | 105/92/1110/1071/62/35; sem importação/ativação |
| AC19 testes/CI/auditoria/evidência | **PARTIAL** | testes locais PASS; CI e auditoria registrados após o push |

## 8. Bloqueio e ação necessária

**BLOCKED_DOCKER_DESKTOP_ABSENT.** O host tem Windows 11, WSL2 e virtualização, mas não tem Docker Desktop nem Docker CLI/daemon. Instalar Docker Desktop/habilitar recursos exige ação administrativa e provavelmente reinício, o que este Work Order não executa sem autorização.

Ação mínima do proprietário:
1. Autorizar/instalar Docker Desktop com backend WSL2 neste Windows 11.
2. Confirmar `docker version` e `docker compose version`.
3. Executar `scripts/windows/Initialize-PaperclipSecrets.ps1` (os segredos já existem; não rotacionar).
4. Executar `scripts/windows/Start-Paperclip.ps1`.
5. Abrir `http://localhost:3100`, reivindicar a instância no navegador e **não** criar agentes.
6. Executar status, parada/início para persistência, backup, restauração isolada e verificação de exposição.
7. Atualizar o Evidence Bundle com run de CI, health e logs; então auditoria independente e eventual APPROVED.

Nenhum acesso à VPS, SSH, firewall/NSG/DNS, deploy ou segredo remoto foi executado.

## 9. Checkpoint Delta proposto

**`LOCAL_FIRST_IMPLEMENTATION_PREPARED_RUNTIME_BLOCKED_DOCKER_ABSENT`**

- Decisão LOCAL FIRST registrada; implementação e testes estáticos/offline completos.
- Runtime Paperclip não instalado por ausência de Docker Desktop; bloqueio externo explícito.
- Nenhuma promoção de checkpoint, merge ou avanço para NLE-SR-WO-001.
- Próximo WO após APPROVED e runtime validado: **NLE-SR-WO-001** (registry schema, locks, quarentena e validador). Não iniciar.

## 10. Veredito

**BLOCKED** — exclusivamente no pré-requisito Docker Desktop/WSL2. A implementação está preparada, os testes locais passam e os segredos estão protegidos; o Paperclip não foi iniciado e nenhuma evidência de runtime é declarada.
