# Requirements
| ID | Requisito | Evidência obrigatória |
|---|---|---|
| REQ-01 | Identidade e catálogo 105/92/1110/62/35 sem renomear IDs | validação bijetiva, fingerprint, cobertura |
| REQ-02 | Paperclip como dono de estado operacional; Git dono de políticas/skills | capability matrix pinada, read-back, sem escrita DB upstream |
| REQ-03 | Execução sob demanda, fila durável, lease, fencing, dedupe e reconciliação | testes de falha e duplicidade |
| REQ-04 | US$0 incremental, quotas e no-paid-fallback | teste negativo e prova de billing/limites |
| REQ-05 | Skills portáteis, versionadas, qualificadas, mount read-only | SR01–SR06 e locks por agente |
| REQ-06 | RAG híbrido, grafo relacional, seis memórias, claims rastreáveis | 48 cenários INT, testes ACL e benchmark |
| REQ-07 | Isolamento cliente/projeto e privilégio mínimo | canários cross-tenant, RLS e sandbox |
| REQ-08 | Aprendizado candidato, revisão independente e rollback | bloqueio de autopromoção e alterações críticas |
| REQ-09 | CRM, software, marketing, e-books, finanças, research, operações | 62 workflows, gates e evidência ponta a ponta |
| REQ-10 | 35 superfícies Obsidian responsivas e acessíveis | 59 cenários CC, WCAG 2.2 AA, mobile real |
| REQ-11 | VPS ARM64, Windows/Codex, rede privada, recuperação | 32 cenários INFRA, benchmark e restore |
| REQ-12 | Engenharia e auditoria conforme fluxo aprovado | WO, Context Lock, PR, CI, Evidence Bundle, checkpoint |
| REQ-13 | Web3 e financeiro apenas ambientes isolados/simulados | testes de ausência de credenciais e rotas reais |
| REQ-14 | Indicadores sem fabricação, origem, freshness, real/simulado | reconciliação, N/A, contratos de dados |
| REQ-15 | Aprovação humana vinculada a ação e versão | autorização server-side, expiração/replay/TOCTOU negativos |
Detalhes por agente/pacote/workflow/tela e thresholds permanecem nos snapshots; nenhuma redução dos critérios herdados. Metas propostas não são medições.
