# NexLabs Skills Registry | NLE-SKILL-PLAN-001

Estado: PROPOSED / planejamento, não software implantado. Fonte: catálogo 105 agentes v1.0.0-proposed, fingerprint em SOURCE-CATALOG.sha256. Não altera o catálogo original. Sem novas despesas, instalações, publicações ou operações financeiras.

## Inventário
- 1.110 atribuições preservadas, 996 rótulos literais distintos, 1.071 registros contextuais (rótulo dentro do pacote).
- 92 especificações de pacote: 80 domínio + 12 compartilhadas. 101 atribuições em pacotes compartilhados. 183 vínculos agente/pacote.
- 316 testes individuais existentes preservados, mais 92 cenários de pacote propostos; 8 competências core originais são baseline adicional, não contadas nas 1.110 atribuições.
- Nenhum pacote implementado, instalado ou qualificado. Os SPEC.md não são SKILL.md e não podem ser importados como skills de produção.

## Arquivos
- registry.json: inventário, competências contextuais, fontes e contratos de pacotes.
- assignment-matrix.csv: rastreabilidade linha a linha, com contexto original.
- agent-bindings.json: vínculos, limites e avaliações individuais; não é payload nativo Paperclip.
- source-candidates.json: candidatos e referências, não allowlist de produção.
- packages/*/SPEC.md: contrato, competência, entrega, cenário negativo e IDs de testes herdados.
- validate.py: verificação estrutural determinística, sem rede. Execute `python validate.py /caminho/NexLabs_AI_Enterprise_Agent_Catalog.json`.

## Arquitetura proposta / decisões pendentes
ADR-SR-001: Git como fonte de verdade, Paperclip como projeção operacional. Nenhuma edição direta em produção; sugestões de agentes entram por PR.
ADR-SR-002: padrão Agent Skills (https://agentskills.io/specification). Agrupar por procedimento/coerência, não por palavra. Pacotes podem ser divididos após qualificação se gatilhos colidirem. IDs de atribuição permanecem rastreáveis. Mesmo rótulo em contextos diferentes não implica equivalência. A competência compartilhada tem procedimento base e contexto de domínio obrigatório.
ADR-SR-003: sem auto-update de upstream; fonte de terceiros em quarentena com licença específica, SHA completo, hash de bytes, inventário e diff revisados. Nenhum acesso automático por popularidade. Preservar atribuição e obrigações de redistribuição. Se licença ambígua, autoria original ou bloqueio.
ADR-SR-004: permissões fora do prompt, interseção de agente/tarefa/ambiente/política. Skill não concede ferramenta, token, rede ou identidade. Sem live trading, wallets, mainnet, anúncios pagos ou dados pessoais reais. ARGUS revisa de forma independente; para ARGUS, revisor distinto do autor e escalação ao proprietário quando necessário.
ADR-SR-005: pacotes imutáveis por versão + hash, lock por agente, atualização canário e rollback. Versionamento SemVer: major quebra de contrato/gatilho/permissão, minor competência compatível, patch correção sem mudança de contrato. Qualquer alteração de permissão ou risco exige revisão independentemente da versão.

## Estrutura futura de pacote qualificado
```
skills/nle-<slug>/
  SKILL.md                # YAML name/description + procedimento e gatilhos
  references/             # fontes versionadas e runbooks necessários
  scripts/                # opcional; código auditado, execução explícita
  assets/                 # opcional; templates e schemas
registry/
  manifests/<slug>.json   # versão, hashes, SBOM, licença, dono, dependências, risco
  locks/<agent-id>.json    # versão/hash exato, modelo/adapter, ambiente e gates
  evaluations/<slug>/     # fixtures sintéticas, golden sets, asserts e casos negativos
  evidence/<release>/     # relatório, custo/latência, resultado e veredito
```
`SKILL.md` usa name igual ao diretório, descrição de gatilho e contraexemplos. Não carregar referências até necessidade. Campo allowed-tools não é mecanismo de segurança; broker aplica policy. Não embutir segredos ou dados de clientes. Skills base cobrem verificação de fonte, comunicação, segurança, contexto, uso mínimo de ferramentas, incerteza, handoff e escalação de bloqueios; incluir explicitamente nos manifests de qualificação, sem contagem dupla.

## Ciclo de vida
DISCOVERED → QUARANTINED → SPECIFIED → IMPLEMENTED → STATIC_VERIFIED → SANDBOX_VERIFIED → INDEPENDENT_REVIEW → APPROVED → STAGED → ACTIVE → DEPRECATED/REVOKED. Nenhuma transição implícita. Atualização volta a avaliação conforme impacto. Revogação cancela novos runs, isola execução em curso, restaura versão anterior aprovada ou suspende agente.

## Gates SR01–SR06
1. SR01 Proveniência: commit imutável, hash, licença individual, inventário, dependências, escopo e custo verificados. Sem scripts remotos, downloads opacos, symlinks escapando do workspace ou licença incompatível.
2. SR02 Estrutura: parser YAML seguro, schema, nome/diretório, referências locais existentes, IDs exclusivos, dependências sem ciclos, matriz sem órfãos; análise de conteúdo, scripts e dependências (SCA, SAST, segredos, SBOM conforme risco).
3. SR03 Segurança: execução em sandbox com rede negada por padrão, credenciais sintéticas, ferramenta não autorizada bloqueada no gateway. Testar prompt injection, exfiltração, path traversal e escalada de privilégio. Nenhuma instalação por script sem revisão.
4. SR04 Qualidade: fixtures de domínio, golden set congelado, gatilhos positivos e negativos, contraprova, evidência e replay. Cada competência tem cobertura explícita por teste individual ou composto; não assumir que 92 cenários provam 1.071 competências. Avaliar modelo+skill contra modelo sem skill, com custo e latência comparáveis. Proposta: 90/100, todos os testes obrigatórios e zero HIGH/CRITICAL; repetir casos estocásticos pelo menos 3 vezes como mínimo inicial, ampliar amostra para high assurance. Metas estatísticas por domínio antes da execução, não alegar significância a partir de 3 runs.
5. SR05 Integração: conferir import/assign/read-back e bytes no executor, isolamento por workspace e política; teste de ausência de skill, versão errada, conflito e adapter unsupported. Testar recuperação e revogação.
6. SR06 Auditoria: executor e auditor independentes; Evidence Bundle com base/head SHA, versão de skill, modelo resolvido, adapter, fixture/hash, logs redigidos, resultados, custos, licenças, riscos e checkpoint delta. APPROVED somente com todos os gates exigidos; owner decide políticas críticas.

## Integração Paperclip
Documentação: https://docs.paperclip.ing/reference/skills/ e https://docs.paperclip.ing/reference/cli/agent/ . Importação da biblioteca e associação ao agente são operações distintas. O CLI skills:sync substitui o conjunto desejado; calcular diff, preservar skills obrigatórias e validar read-back. Adaptadores podem sincronizar no workspace, durante run, ou apenas registrar intenção. Testar os bytes efetivamente carregados. Pin por versionId depende da configuração experimental enableBetaSkills na documentação consultada: não ativar automaticamente; alternativa é usar artefatos de versão imutáveis em workspace e bloquear divergência por hash, somente após prova de compatibilidade. Desabilitar atualização automática de fontes externas. API versionada e versão instalada ainda não verificadas. Usar mock antes de conexão real.

## Backlog / ordem dos incrementos
- NLE-SR-WO-001 NECESSARY: baseline Source Pack/ADR/Context Lock, schema, validador, locks, quarentena, policy e CI local. Sem implementar 92 pacotes de uma vez.
- NLE-SR-WO-002 NECESSARY: 12 core packages, harness de avaliação, segurança do tool gateway e qualificação em sandbox.
- NLE-SR-WO-003 NECESSARY: piloto engenharia/governança com engineering-governance, software-testing, software-audit e frontend-engineering; importar apenas candidatos aprovados.
- NLE-SR-WO-004 NECESSARY: piloto comercial/marketing com b2b-prospecting, content-strategy, search-optimization e marketing-measurement; drafts e dados sintéticos.
- NLE-SR-WO-005 NECESSARY: produtos digitais e e-commerce, mock checkout e artefatos validados.
- NLE-SR-WO-006 NECESSARY: demais domínios corporativos, segurança e pesquisa; expansão em lotes pequenos com gates.
- NLE-SR-WO-007 NECESSARY: Web3 e finanças HIGH_ASSURANCE; testnet local, backtesting e paper trading isolados.
- NLE-SR-WO-008 NECESSARY: qualificação dos 105 agentes, 316 cenários, cobertura de competências, canário, rollback e auditoria final.
- IMPORTANT: melhoria baseada em telemetria, comparação de modelos. FUTURE: marketplace interno e auto-sugestão de skills. OUT OF SCOPE: execução financeira real, compra de infraestrutura ou ampliação de licenças.

## Definition of Done da versão completa
100% das atribuições reconciliadas; todas as competências implementadas e cobertas por provas rastreáveis; todos os pacotes ativos com versão e licença verificadas; todos os 105 agentes com testes individuais e gates aprovados; nenhuma permissão implicitamente concedida, nenhuma falha HIGH/CRITICAL, nenhuma nova despesa; rollback, revogação, backup/restore e read-back comprovados. Código, documentação, CI, implantação e validação de ambiente real autorizada. Estado atual: planejamento estrutural, DoD operacional NÃO satisfeito.
