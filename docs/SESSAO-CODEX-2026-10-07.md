# Sessão Codex — 07/10/2026, manhã

Retomada a partir de CONTINUACAO-CODEX.md e do trabalho Claude b831d70.
Objetivo desta etapa atingido: primeiro carregamento visível do Fusion 2018 no
Carbon, por instalação reversível no MUSTANGGT. Não é aprovação de release.

## Compilação e correções

1. Preservada a saída anterior em `work/carbon-compiler/before-axes/`.
2. nfscgc confirmou que lê todos os OBJ da pasta ao selecionar BASE_A.obj;
   não exige seleção manual dos 351 arquivos. matlist/mpoints/link foram carregados.
3. OBJ de pontos gerados pelo Claude não tinham UVs: erro “Not found the texture
   coordinates”. O gerador foi ajustado para UVs/normais e nome de grupo `_MARKERnn`
   igual ao mpoints.txt. A tentativa posterior processou os 165 pontos.
4. O gerador não apaga mais recursivamente a pasta de saída: a GUI mantém o diretório
   aberto e rmtree falhava por lock após remover o conteúdo. Agora sobrescreve os
   arquivos gerados, preservando a pasta. Usar uma pasta nova quando mudar o conjunto
   de peças para não deixar OBJ antigos. Origem e destino não podem ser iguais.
5. A orientação pré-girada passou: BODY_A X −2.364096→2.368057, Y −1.0413111→1.0387574,
   Z −0.04379161→1.2634124; lanternas na traseira X negativo; pneu com largura em Y.
6. Primeira saída corrigida: 186 sólidos e 165 marcadores em 40 sólidos; posições
   dentro de 1 mm, porém 20 matrizes divergiam do doador em faróis/freios/spoilers.

## Preservação das matrizes oficiais

`scripts/apply-donor-marker-matrices.py` aplica os primeiros 12 componentes das
matrizes do MUSTANGGT instalado aos marcadores, mantendo nomes e translações Fusion.
Usa a mesma peça do doador quando disponível; quando falta (ex.: BASE_E e KIT01_BODY),
usa BASE_A, KIT00_BODY_A ou KIT00_FRONT_TIRE_A oficiais conforme a família. A origem
de cada matriz fica em `docs/carbon2018-marker-matrix-remap.json`.

A saída nfscgc desta compilação já contém CIP (187 entradas com sentinel). Foi
descomprimida pelo extrator e remontada com streaming CIP/RAWW sem perda. A tentativa
intermediária de streaming direto sem CIP não foi reconhecida pelo CarToolkit;
nunca foi instalada. O arquivo para reexportar é:
`work/carbon-compiler/geometry-donor-matrices.bin`.

CarToolkit reconheceu 186 sólidos reais, reexportou para Carbon e retirou o sentinel.
Os leitores independentes confirmaram todas as malhas e os 165 marcadores, incluindo
as matrizes esperadas e translações. Os nomes/triângulos correspondem ao source-report;
máximo 65397 índices. As texturas reutilizadas têm o mesmo hash anterior, 10 entradas
válidas. Relatório final: `docs/carbon2018-stage-axes-verification.json`.

## Instalação experimental ativa

- `scripts/test-install-2018.ps1 -Action Install` executado às 10:01 locais.
- Pasta completa MUSTANGGT preservada em `CARS/MUSTANGGT_backup_stock/` e seus
  três BIN conferidos contra `reference/carbon-stock/MUSTANGGT/`.
- Somente GEOMETRY.BIN/TEXTURES.BIN substituídos. VINYLS preservado.
- GLOBAL e CAMARO conferidos contra referência: intactos. Nenhuma edição VLT/FE.
- Nome de seleção/FE continua Mustang GT; tração/performance stock permanecem.
- Instalação registrada em `docs/carbon2018-test-install.json`.

O jogo foi aberto por Codex. Foi detectada entrada do usuário, e a captura seguinte
mostrou o Fusion azul na câmera do jogo com carroceria e rodas. Codex deixou o
controle com o usuário. A imagem original foi preservada em
`capturas/2018/primeiro-teste-carbon-2026-10-07.jpg`, com manifesto e hash.

Observado: carro e rodas carregaram; sem substituição visual pelo Carrera GT nessa
captura. Há manchas/artefatos em superfícies, vidros e adesivos. Causa ainda não
isolada: revisar materiais/effects, cores de vértices, sobreposição de peças e
VINYLS/UV antes de atribuir o defeito a um componente específico.
Não foram testados corrida, kits, damage, IA, dirigibilidade ou início da carreira.

## Reprodução da etapa

```powershell
python scripts/prepare-compiler-input.py
# Compilar source-axes no nfscgc; preservar backup antes de sobrescrever geometry.bin.
# Regenerar docs/carbon2018-axes-compiled-inventory.json para o novo BIN.
pwsh -NoProfile -File scripts/extract-carbon-solids.ps1 -InventoryFile docs/carbon2018-axes-compiled-inventory.json -OutputRoot work/carbon2018-axes-compiled-solids
python scripts/apply-donor-marker-matrices.py work/carbon-compiler/geometry.bin work/carbon-compiler/geometry-donor-matrices.bin
# CarToolkit: abrir geometry-donor-matrices.bin; Carbon/Racer/MUSTANGGT;
# exportar em work/carbon2018-stage-axes. Reutilizar TEXTURES.BIN anterior.
# Regenerar inventário staging para o novo BIN antes de extrair.
pwsh -NoProfile -File scripts/extract-carbon-solids.ps1 -InventoryFile docs/carbon2018-stage-axes-inventory.json -OutputRoot work/carbon2018-stage-axes-solids
pwsh -NoProfile -File scripts/validate-carbon-solids.ps1 -InputRoot work/carbon2018-stage-axes-solids -OutputFile docs/carbon2018-stage-axes-audit.json
python scripts/dump_position_markers.py work/carbon2018-stage-axes-solids/carbon2018-stage-axes docs/carbon2018-stage-axes-audit.json docs/carbon2018-stage-axes-markers.json
python scripts/verify-carbon-axes.py
pwsh -NoProfile -File scripts/validate-carbon-textures.ps1 -InputFile work/carbon2018-stage-axes/TEXTURES.BIN -OutputFile docs/carbon2018-stage-axes-texture-audit.json
```

Inventários: usar inventory(path, carbon=True, extracted_root=...) do script
inventory_geometry.py. Na primeira leitura de BIN novo, usar raiz vazia para não
misturar sólidos extraídos de uma versão anterior; depois regenerar com os novos sólidos.

## Reversão e próximo trabalho

Fechar NFSC antes de alterar os BIN. Restaurar:

```powershell
pwsh -NoProfile -File scripts/test-install-2018.ps1 -Action Restore
```

Restore só depende do backup/referência, não da validade do staging. O script recusa
mudanças enquanto NFSC está aberto, verifica hashes e preserva VINYLS.
Para reaplicar a versão auditada, usar Install; este verifica os hashes do staging.

Próximo: isolar os artefatos visuais com o usuário, testar carro stock/kit00 e corrida,
completar lacunas de peças e montagem. LICENSEPLATE/ROOF_SCOOP/escapes de para-choque
e recursos AutoSculpt/damage permanecem pendentes. Origem vanilla dos doadores ainda
é sustentada por evidência local, sem comprovação independente de instalação limpa.
Depois FE/performance no VltEd, decisão RWD/AWD 2018 e port 2012 → CAMARO.

## Continuação após confirmação do usuário — 10:07–10:20

Usuário confirmou que o 2018 apareceu e autorizou prosseguir. Diagnóstico:
- `diagnose-carbon-surfaces.py`: nomes de materiais pelo dicionário do compilador,
  cores e slots de textura MW, comparação de triângulos BASE/KIT00 de LOD A.
  Nenhum triângulo exatamente igual entre BASE/BODY/HOOD na fonte, com arredondamento
  de 10 micrômetros. Não exclui proximidade, simplificação ou peças simultâneas.
- Oito hashes de adesivos sem nome continuam sem adaptação ao GLOBAL Carbon.
- Auditoria de atributos independente: saída OBJ inteira branca; fonte tem 55
  cores no material DECAL, e valores diferentes em freios. Normais não finitas: zero;
  730 normais zeradas e tangentes zeradas em CarShader. O doador também tem atributos
  problemáticos segundo o leitor; não assumir causalidade sem teste isolado.

`restore-carbon-vertex-colors.py` recupera atributos por posição/UV com tolerância
máxima de 2 micrômetros no fallback; aborta se ausente ou ambíguo. Mudou 552 cores
em 14 sólidos, preservando os demais bytes. BIN intermediário CIP/RAWW reexportado
pelo CarToolkit em `work/carbon2018-stage-colors`. `verify-carbon-colors.py` confirma
que os 186 sólidos reexportados são exatamente os sólidos corrigidos, auditoria
mesh/material idêntica à versão axes e TEXTURES idêntico. Marcadores preservados
pela identidade dos bytes. Relatórios em `docs/carbon2018-stage-colors-*`.

Instalação reversível às 10:18 com `test-install-2018.ps1`, agora aceitando
`-VerificationFile docs/carbon2018-stage-colors-verification.json`. O parâmetro
padrão continua instalando stage-axes. Backup oficial local preservado/verificado.

Carbon aberto novamente. Observação de fotografia mostra Fusion/rodas, mas as
faixas cinzas e artefatos na pintura continuam. Recuperar cores é uma correção
de dados, não uma solução visual comprovada. O usuário já operava a câmera; ao
pedir leitura após detecção de input, o helper informou interrupção física com
Escape. Encerradas as ações Computer Use. Sem corrida, kit ou damage testados.

Próxima etapa: adaptar adesivos e materiais ao MUSTANGGT oficial, isolar possível
proximidade entre malhas/simplificação, depois testar stock/kit00 e corrida. Não
usar outro mod como doador. Documentação preserva limites da conclusão.
