# Test / Benchmark Plan
Bootstrap: verificação SHA256 dos originais, integridade ZIP e igualdade bytes extraídos, catálogo vs matriz, hierarquia sem ciclos, conjuntos e referências, testes de reviewer segregation, status desativado, limites US$0. Testes negativos por mutação sintética; sem execução de builders históricos. CI sem rede externa além do checkout, sem secrets, permissões read-only e runner/quotas verificadas antes de habilitar. Evidências atuais exclusivamente locais.

| Família | Especificações herdadas | Gate |
|---|---:|---|
| Agentes | 316 cenários + 525 instâncias de 5 gates | 90/100 e todos os gates, zero falha crítica |
| Skills | 92 cenários de pacote + SR01–SR06 | proveniência/licença, segurança, qualidade, integração, auditoria |
| Workflows | 434 instâncias (62 específicos + 372 comuns) | efeitos, idempotência, quotas, reviewer, recuperação |
| Intelligence | 48 | RAG, grafo, segurança, learning, contexto, restore |
| Infraestrutura | 32 | compatibilidade, quotas, isolamento, rede, backup, restore |
| Command Center | 59 | contratos, dados, UI, mobile, acessibilidade, segurança |
Contagens são inventário de especificações, não testes executados nem necessariamente casos independentes; não somar como cobertura real. Preserve IDs herdados, crie fixtures, oráculos determinísticos e logs por caso. Testes LOW direcionados; STANDARD unit/lint/typecheck/build/integração; ELEVATED regressão, migração, recuperação; HIGH_ASSURANCE proof obligations, negativos adversariais, revisão independente, rollback. Model judges auxiliares, não prova única; comparar baseline/candidato com casos congelados e holdout. Recall@10 ≥90%, Precision@5 ≥80%, citações válidas 100%, claims sustentados ≥95%, críticos 100%, abstention ≥95%, economia mediana entrada ≥30% sem regressão relevante: metas do plano INT, exigem medição. Quotas desconhecidas não permitir benchmark automático pago. UI performance e acessibilidade conforme CC original. Evidence Bundle com base/head, versões/hashes, comandos, resultado e falhas, logs sanitizados, riscos e checkpoint delta.
