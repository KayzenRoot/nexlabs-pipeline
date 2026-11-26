# Definition of Done
## Bootstrap gate (não é release)
B01 remote/namespace/private/base SHA e permissões confirmados; B02 seis pacotes preservados byte a byte, 105/92/1110/62/35 e IDs validados; B03 decisões ratificadas registradas sem transformar propostas em aprovações de runtime; B04 Source Pack completo e backlog sem lacunas/duplicação; B05 Context Lock real, validação local e CI gratuito qualificado; B06 governança GitHub read-back e política US$0; B07 Evidence Bundle com riscos/erros/diff, auditoria independente APPROVED e checkpoint delta; B08 merge squash somente após gates e read-back. Se qualquer gate faltar, não declarar bootstrap integrado.
## v1.0 gate
D01 105 identidades qualificadas e 92 pacotes reais versionados, 1110 atribuições preservadas; D02 62 workflows qualificados em escopo permitido, gates e efeitos externos testados; D03 Intelligence Hub RAG/grafo/memória/learning, isolamento e metas INT provados; D04 35 superfícies reutilizadas/implementadas, acessibilidade e mobile; D05 Oracle/Windows, quotas, filas, backups, RPO/RTO medidos e recuperação; D06 segurança, ausência de HIGH/CRITICAL conhecidos, HIGH_ASSURANCE e segregação; D07 integrações autorizadas e US$0 incremental comprovado, limitações explícitas; D08 evidências, docs canônicas, CI, auditoria, deploy privado autorizado, smoke/read-back, checkpoint final. Limitações de fornecedor sem alternativa suportada são BLOCKED ou alteração de escopo ratificada, não marcar concluído. Sem produção real, trades, mainnet ou gastos por inferência. Release só termina FUNCIONAL + TESTADA + DOCUMENTADA + DEPLOYADA + VALIDADA no escopo autorizado.

## Status CD-02/CD-03 | 2026-11-26
- B01: target/ID/base/permissões verificados; a exigência original de repositório privado é superseded apenas por NLE-ADR-BOOT-007 para desenvolvimento revisado e não sensível; produção permanece privada. **PASS no escopo do bootstrap.**
- B02: 364/364 originais, seis ZIPs e fingerprints SHA-256 conferem; 105/92/1110/62/35 e 1.071 registros preservados. **PASS.**
- B03: decisões ratificadas e hierarquia preservadas; propostas não convertidas em aprovação. **PASS.**
- B04: Source Pack completo e 40 WOs de domínio no backlog, sem duplicação. **PASS.**
- B05: Context Lock real, validação local 7/7 + 7/7 PASS e CI gratuita **EM QUALIFICAÇÃO** no runner padrão `ubuntu-24.04`. **PENDING_FIRST_RUN.**
- B06: proteção da `main` e squash-only com read-back; check `docs-validation` será exigido após a primeira execução bem-sucedida. **PARTIAL/PENDING.**
- B07: Evidence Bundle e auditoria independente **PENDING**, sem APPROVED. **PENDING.**
- B08: merge squash **NOT_DONE**; somente após APPROVED e read-back. **PENDING.**
Conclusão: bootstrap **não integrado**. Pendências: primeira execução de CI, read-back do check obrigatório e auditoria independente. Nenhuma aprovação de implementação, runtime, deploy ou gasto é inferida.
