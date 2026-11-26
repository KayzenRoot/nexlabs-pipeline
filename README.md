# NexLabs AI Enterprise | NLE-BOOTSTRAP-001
Fundação candidata v1.0.0-plan. **Não implantada.** Target: `KayzenRoot/nexlabs-pipeline` (ID 1472951510). Desenvolvimento público temporário autorizado por NLE-ADR-BOOT-007 apenas para material revisado e não sensível; produção permanece privada.

## Estado CD-03
- Source Pack completo: 364/364 originais e seis ZIPs, com `locks/source-lock.json` (SHA-256 `a72bc69bd3da2e456205d6cb98776c002cff53800d70efa9ea70b3ebd648231e`).
- Validador canônico e testes: 7 grupos PASS e 7/7 testes PASS em execução local; CI remota em qualificação.
- Git: base `48d3e422313f869992d09b99f0b7e09acd4e1caa`, branch `chore/nle-bootstrap-001`, PR #1 draft. HEAD auditado em `locks/context-lock.json`; HEAD final no Evidence Bundle.
- Governança: `main` com PR obrigatório, histórico linear, sem force/delete, squash-only e sem bypass; check obrigatório `docs-validation` em qualificação.
- CI: workflow mínimo `docs-validation`, runner padrão `ubuntu-24.04`, sem secrets, cache, artefatos ou deploy; primeira execução pendente.
- Proveniência e estado Git separados em `docs/Provenance.md`.
- Auditoria independente: PENDING. Merge, deploy e ativação de agentes: NÃO AUTORIZADOS.

## Source Hierarchy
1. Checkpoint aprovado (`docs/Checkpoint.md`)
2. Decisions Ledger/ADRs (`docs/Decisions-Ledger.md`)
3. Scope (`docs/Scope.md`)
4. Definition of Done (`docs/Definition-of-Done.md`)
5. Architecture (`docs/Architecture.md`)
6. Requirements (`docs/Requirements.md`)
7. Demais documentos, snapshots e fontes externas qualificadas.
Código, Git, testes e evidências prevalecem sobre memória ou afirmações não comprovadas. Contradições são BLOCKED ou Correction Delta; não sobrescrever decisão aprovada. Este pacote é candidato, não aprovação de implementação. Proveniência do pacote e estado Git remoto são cadeias distintas; ver `docs/Provenance.md`.

## Como usar
- Leia `docs/Checkpoint.md`, `docs/Decisions-Ledger.md`, `docs/Consistency-Audit.md`, `docs/Backlog.md`, `work-orders/NLE-BOOTSTRAP-001.md` e `prompts/NLE-BOOTSTRAP-001-CODEX.md`.
- Execute `python scripts/validate_sources.py` e `python -m unittest discover -s tests -v` em raiz (Python 3.10+, biblioteca padrão, sem rede).
- `sources/` contém seis ZIPs intactos, seus arquivos extraídos sem alterações e originais avulsos. Não execute `build.py` antigos: são registros históricos, podem depender de caminhos locais. Não importe SPEC.md como SKILL.md. `locks/source-lock.json` fixa os bytes; `locks/context-lock.json` fixa a base, o lock e os fingerprints canônicos desta execução.
- `docs/Backlog.md` é sequência única; os 40 IDs de domínio são preservados. Não existe autorização de runtime nem de expansão de escopo por esta entrega.
- Evidências locais em `evidence/`; CI remoto, revisão independente e merge pendentes. `locks/remote-context-lock.json` e `evidence/remote-import.md` são registros históricos do CD-02 parcial, preservados.
- CI: `.github/workflows/docs-validation.yml` executa o validador e os 7 testes em `ubuntu-24.04` com `contents: read`, checkout pinado e sem secrets/cache/artefatos. A proveniência do pacote e o estado Git estão separados em `docs/Provenance.md`.
