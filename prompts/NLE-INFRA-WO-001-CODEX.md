# NLE-INFRA-WO-001 | Codex one-shot execution

Você está executando no Windows 11 do proprietário. Faça somente o inventário read-only deste Work Order. Não instale, configure, inicie, pare, atualize ou exponha serviço algum.

## Objetivo
Executar os dois coletores versionados:
- scripts/infra/collect_windows_inventory.ps1 no Windows local.
- scripts/infra/collect_vps_inventory.sh na VPS Oracle Ubuntu ARM64, transmitido por stdin através de um alias SSH já configurado.

## Regras absolutas
- Não instalar nada e não usar sudo.
- Não criar nem alterar contas, chaves, tokens, secrets, firewall, NSG, portas, volumes, swap, Docker, WSL, WireGuard ou serviços.
- Não executar Paperclip, criar empresa, cadastrar agentes, ativar Runner, habilitar Environments, rotinas ou workflows.
- Não ler arquivos .env, variáveis de ambiente, tokens, cookies, chaves privadas, logs, argumentos de processos ou conteúdo de secrets.
- Não mostrar hostname, endereço IP, username, caminho de chave SSH, nome de container ou output bruto no GitHub.
- Não salvar os relatórios brutos no repositório. Eles são infraestrutura sensível e devem permanecer em diretório local fora do clone.
- Não inventar medidas ausentes. Use UNKNOWN quando uma verificação não puder ser feita.
- Se qualquer ação exigir mutação, instalação, pagamento ou autorização adicional, pare.

## Preflight do repositório
1. Localize o clone cujo remote aponta exatamente para KayzenRoot/nexlabs-pipeline. Se não existir clone, faça clone do repositório público em diretório de trabalho próprio, sem tocar em outros projetos.
2. Confira git status. Se houver alterações locais não relacionadas, não as sobrescreva; use outro clone ou pare.
3. Faça fetch e checkout da branch work/nle-infra-wo-001. Não crie branch concorrente.
4. Confirme que o HEAD deriva de 8321110a2ff29aec90ffc1c384ea21f722de0497 e que o Context Lock está presente.
5. Execute:
   - bash -n scripts/infra/collect_vps_inventory.sh (se Bash estiver disponível)
   - python scripts/validate_sources.py
   - python -m unittest discover -s tests -v
   Corrija somente falhas introduzidas neste Work Order. Não modifique snapshots em sources/.

## Inventário Windows
1. Crie um diretório local fora do repositório em %LOCALAPPDATA%\NexLabs\NLE-INFRA-WO-001.
2. Execute:
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/infra/collect_windows_inventory.ps1
3. Valide que a saída é JSON e salve-a em windows-inventory.raw.json dentro do diretório local.
4. O script só classifica o status de login do Codex. Não tente autenticar, renovar sessão ou abrir login.
5. Não copie a saída bruta para o repositório, PR, chat ou logs públicos.

## Inventário VPS
1. Examine somente os nomes dos aliases Host em %USERPROFILE%\.ssh\config. Não imprima o arquivo nem leia chaves privadas.
2. Se houver exatamente um alias plausível para a VPS (por exemplo, nome contendo oracle, vps, nex, arm ou ubuntu) e a configuração resolvida usar o usuário nexdev, selecione-o. Se houver zero ou mais de um candidato, pare e informe apenas que o alias está ausente/ambíguo. Não adivinhe IP ou hostname.
3. Teste conexão em modo não interativo e com timeout:
   ssh -o BatchMode=yes -o ConnectTimeout=8 ALIAS "test -r /etc/os-release && printf VPS_READ_ONLY_PREFLIGHT_OK"
   Não imprima host, usuário ou configuração SSH.
4. Transmita o script pela entrada padrão, sem copiar arquivo para a VPS:
   Get-Content -Raw scripts/infra/collect_vps_inventory.sh | ssh -o BatchMode=yes -o ConnectTimeout=8 ALIAS "bash -s"
5. Salve o output somente em vps-inventory.raw.txt no diretório local criado acima. Não use sudo.
6. Se a conexão falhar, não tente alterar SSH, firewall, WireGuard, NSG ou credenciais. Marque VPS como BLOCKED e pare a parte remota.

## Qualificação
Compare os relatórios com os critérios do Work Order e do plano de infraestrutura:
- VPS: Ubuntu 24.04, ARM64/aarch64, glibc >=2.39 para o Paperclip Runner nativo, CPU, MemAvailable >=2 GiB, swap, filesystem livre >=55 GiB e >=20%, inodes, Docker/Compose, containers, uso de recursos, portas em wildcard, UFW, WireGuard e serviços existentes.
- Windows: Windows 11, CPU/RAM/GPU, espaço livre, WSL2, Docker/Compose, Codex CLI e status de login, Git, SSH e portas em wildcard.
- Diferencie compatibilidade da imagem Docker do servidor Paperclip e compatibilidade do Runner no host onde cada agente executa. Windows nativo não deve ser presumido como Runner compatível.
- Remote Environments/SSH do Paperclip são experimentais; não habilite essa função neste WO.
- OCI NSG/security lists, billing e quotas da conta não são provados por comandos locais. Marque UNKNOWN até read-back autorizado no console.
- Não instale, puxe ou execute imagens. Não faça scans externos. Não habilite serviços.

## Evidência redigida
1. Calcule SHA-256 dos dois relatórios brutos locais.
2. Crie evidence/NLE-INFRA-WO-001-CD01-SUMMARY.md contendo somente:
   - data da coleta;
   - VPS: PASS/FAIL/UNKNOWN para cada critério, sem valores de host;
   - Windows: PASS/FAIL/UNKNOWN para cada critério, sem valores de host;
   - Paperclip Docker ARM64: DOCUMENTED_NOT_HOST_VERIFIED;
   - Runner ARM64/glibc: PASS/FAIL/UNKNOWN conforme medição;
   - Windows Runner: LEGACY_ONLY_EXPECTED;
   - SSH/Sandbox Environments: EXPERIMENTAL_NOT_ENABLED;
   - OCI firewall/NSG e billing/quota: UNKNOWN se não houver read-back autorizado;
   - SHA-256 dos relatórios brutos, sem anexá-los.
3. Não inclua hostname, IP, username, nome de container, caminho local, chave, token, e-mail, saída de comando ou dado pessoal.
4. Execute novamente os testes e o validador.
5. Commit e push somente os arquivos deste Work Order, sem force-push.
6. Atualize a mesma PR de NLE-INFRA-WO-001 se já existir; se não existir, abra uma PR draft com esse título. Não faça merge.
7. Gere Evidence Bundle local e relatório final em português brasileiro com base/head, arquivos, testes, CI, hashes, achados, riscos e AC01–AC09.

## Stop condition
Se não conseguir executar em ambos os hosts, não declare NLE-INFRA-WO-001 concluído. Registre o que foi comprovado, o que ficou UNKNOWN/BLOCKED e pare. Não comece NLE-SR-WO-001, não instale Paperclip e não avance para qualquer outro Work Order.
