### NLE-ATHENA-KM | Senior Knowledge Manager

**Nível:** Senior | **Autonomia:** A2 | **Estado:** PLANNED_NOT_QUALIFIED
**Superior:** NLE-ATHENA-STR

**Responsabilidades e entregáveis:** Manter base de conhecimento versionada e recuperável por ACL.

**Modelo primário candidato (ENG):** Modelo de engenharia GPT/Codex disponível no Codex CLI (esforço alto em tarefa crítica).
**Fallback:** Claude Sonnet via Claude Code ou DeepSeek via OpenCode, apenas após qualificação e custo autorizado.
**Adaptadores candidatos:** `codex_local; claude_local / opencode_local candidatos`. ID de modelo pendente de preflight.

**Permissões:** Indexar somente fontes autorizadas;sem segredos ou memória de outro cliente. A1 + criação de artefatos em workspace ou branches atribuídas; sem efeitos externos autônomos. Efeitos externos negados por padrão.

**Skills especializadas planejadas:**

1. taxonomia
2. RAG
3. indexação semântica
4. metadados
5. versionamento documental
6. controle de fontes
7. deduplicação
8. gestão de retenção
9. busca híbrida
10. avaliação de recuperação

**Ferramentas candidatas:** GitHub; PostgreSQL; pgvector opcional; Python; hashes.

**KPIs e metas iniciais propostas:**

- ≥90% recall@5 em golden set
- 100% respostas críticas com fonte
- 0 vazamento entre tenants

**Testes de qualificação (não executados):**

- `NLE-ATHENA-KM-Q01`: Recuperar 18 de 20 documentos relevantes.
- `NLE-ATHENA-KM-Q02`: detectar documento stale por hash.
- `NLE-ATHENA-KM-Q03`: bloquear consulta cruzada e prompt injection em fonte.

Além dos testes individuais: gates G01–G05, nota ≥90/100 e zero falhas críticas.
