# Passagem para Claude — 07/10/2026 às 02:31

Horário de retomada informado pelo usuário, fuso America/Sao_Paulo (UTC−03:00).
Este arquivo deixa a tarefa pronta para a sessão do Claude; não agenda nem inicia essa sessão.

## Instruções do usuário

- Assumir TODO.md; ao parar, fazer commit e registrar coautoria do agente.
- Usar **CAMARO oficial do Carbon** como doador para o Fusion 2012, e
  **MUSTANGGT oficial do Carbon** para o Fusion 2018. Esses são os veículos substituídos.
- Preservar CAMARON. Trabalhar em pt-BR.

## Trabalho entregue por Codex

- Estrutura mínima e README; referências locais ignoradas no Git.
- ZIPs v2.8 verificados contra os hashes registrados no projeto MW e extraídos.
- Backup dos três BIN de cada slot e dos arquivos diretamente em GLOBAL.
- Manifesto de 73 arquivos e inventário de quatro GEOMETRY.BIN.
- Os sólidos MW estão nomeados no inventário; os doadores Carbon têm 848/997
  entradas CIP comprimidas, ainda sem nomes ou malhas extraídos.
- Utilitários MW selecionados espelhados em tools/vendor/mw; proveniência em
  tools/README.md. Não executar esses compiladores para produzir BIN Carbon.
- Jogo e projeto MW não foram alterados. Sem instalação, release ou QA em jogo.

## Próximos passos, em ordem

1. Ler TODO.md, README.md e os dois manifestos em docs. Executar
   `pwsh -File scripts/prepare-reference.ps1` e `python scripts/inventory_geometry.py`
   se precisar verificar/recriar o setup. Os backups Carbon nunca devem ser sobrescritos
   por arquivos modificados da instalação.
2. Confirmar que os doadores são realmente oficiais/limpos. O Backup do jogo só
   contém localização. As cópias estão rotuladas `carbon-installed-donor-unverified-stock`.
   Se houver mod nos slots, obter os originais da instalação/mídia oficial e registrar
   novos hashes antes de usá-los como base. Não trocar por veículos de outro mod.
3. Providenciar ferramenta com leitura CIP e **exportação Carbon**, por exemplo
   CarToolkit/Carbon ModTools, verificando a documentação e a licença da ferramenta.
   `../fusion-mw2005/tools/NFS-ModTools/Common/Geometry/CarbonSolidListReader.cs`
   documenta a tabela de streaming; `Common/Compression.cs` depende de CompLib.
   O `dotnet` disponível não listou SDKs nesta sessão. Não afirmar que as ferramentas
   necessárias já estão prontas: fontes de leitores não equivalem a exportador.
4. Descomprimir e inventariar os oficiais CAMARO/MUSTANGGT: peças, LODs, kits,
   AutoSculpt, damage, marcadores, materiais e texturas. Comparar com os 202/186
   sólidos MW. Finalizar o mapa de peças ausentes antes de marcar a Fase 0 completa.
5. Começar pelo 2018 → MUSTANGGT; preservar os recursos exigidos pelo slot oficial
   e inserir a malha Fusion. Exportar geometry e textures com alvo Carbon para `work/`.
   Não copiar geometry MW diretamente ao jogo nem tratar RetargetSlot como conversor.
6. Preparar VLT mínimo após inspecionar os nós reais e preservar backup. Não portar
   MWPS literalmente. O 2018 MW está RWD apesar do nome AWD; 2012 exige FWD.
   Confirmar no VLT/FE o uso de CAMARO no início e os nós/variantes antes de editar.
7. Só avançar para instalação/teste com saída Carbon validada; registrar o que foi
   realmente testado. Ao parar, atualizar TODO/passagem e fazer commit com coautoria.

## Fontes exatas

- `reference/mw-v28/Fusion2018_AWD_MW2005/Fusion2018_AWD_MW2005/CARS/MUSTANGGT/`
- `reference/mw-v28/Fusion2012_FWD_MW2005/Fusion2012_FWD_MW2005/CARS/COBALTSS/`
- MWPS em `ADDONS/CARS_REPLACE/<slot>/` dentro de cada pacote extraído.
- `reference/carbon-stock/CAMARO/` e `reference/carbon-stock/MUSTANGGT/`
- `reference/carbon-global-before/`
- Contexto MW: `../fusion-mw2005/docs/APRENDIZADOS.md` e `docs/CONTINUACAO.md`.

O próximo objetivo é obter o mapa das peças oficiais e uma exportação Carbon do
2018 em staging. O port completo segue pendente nas Fases 1–7 de TODO.md.
