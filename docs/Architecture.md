# Architecture
Control plane privado Oracle Ubuntu ARM64: Paperclip (gestão de agentes, tarefas, projetos, runs, aprovações nativas); PostgreSQL (DB/roles separados Paperclip e NexLabs); pgvector/FTS e grafo relacional; Intelligence Hub; gateway modular/worker e fila persistente somente para lacunas comprovadas; 9Router opcional; Netdata existente. Windows: Codex CLI oficial, builds, testes e mídia; WSL2/remote apenas após qualificação. WireGuard como candidato ratificado de direção; não expor DB, Paperclip, 9Router, Docker, Portainer. GitHub canônico. Não presumir HA. Conectividade celular por rede privada.

## Responsabilidade de dados
Paperclip = runtime; Git = código, documentação, skills aprovadas, decisões; NexLabs = CRM/financeiro/ledger de efeitos, memória, avaliações, projeções e dados editoriais. Provedores = dados de campanha, venda e mercado; interface exibe origem e freshness, não duplica autoridade. Nenhuma escrita em DB upstream. Identity gateway valida humano/agente, company, cliente, projeto, workflow, recurso e versão de policy; permissões como interseção, default deny.

## Controles
Uma execução LLM global inicial, um job pesado Windows, um leve/embedding VPS; fila 100 global/20 projeto, no máximo 2 filhos e 3 níveis, lease 120s/renew 30s, fencing e reconciliação antes de retry; rotinas desativadas. RAM caps candidatos 4608 MiB, crescimento 40 GiB; inventário real e serviços existentes prevalecem. Quota 70/20/10 somente se telemetria confiável, pausar normal a 70%, stop 90%; desconhecido bloqueia automatização, sem fallback pago. Codex oficial direto; nenhum proxy de credenciais.

## Intelligence
M0–M5, claims com proveniência, classificação e validade temporal, ACL antes de query/cache/graph expansion. Embedding local candidato E5 Small, exact search primeiro; sem memória cross-client. Aprendizado por candidato → avaliação → auditoria → aprovação independente → canário → release → rollback. Não retreina modelos por padrão.

## Command Center
35 superfícies lógicas, 2 nativas/6 complementadas/27 extensões agrupadas. Obsidian dark, lime/magenta, CSS 3D leve, motion reduzível, WCAG 2.2 AA, React/TypeScript/Vite candidatos. Integração plugin-first condicional segundo documento ratificado; a resposta anterior também propôs sidecar-first. **Não congelar implementação de shell:** CC-WO-001 compara plugin pinado e sidecar privado; ADR de seleção e aprovação antes da implementação. Ambos preservam API oficial, sem fork inicial, sem iframe inseguro, sem duplicação de estado. A rota de fallback sidecar é permitida se plugin não qualificar; não instalar alpha sem autorização.
