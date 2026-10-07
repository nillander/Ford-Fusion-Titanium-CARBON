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

## Lentes e adesivos após revisão do usuário — 10:22–10:29

Usuário informou carroceria boa, sem outras deformações percebidas. Faltam lentes
vermelhas/brancas das lanternas, refletores vermelhos acima dos escapamentos,
faróis e milha; adesivos Mustang deslocados. Preservar a geometria da carroceria.

Comparação local: os oito sólidos GLASS já existem, mas seus materiais compilados
usam flags 0x4180, contra 0x14180 do MUSTANGGT oficial. Shader dianteiro já coincide;
traseiro veio como DULLPLASTIC da fonte e passa a usar BRAKELIGHTGLASS do doador.
Não atribuir causalidade visual até observar o jogo.

prepare-carbon-lenses.py parte do stage-colors e recupera flags dos materiais e
light material hash dos sólidos GLASS; fallback LOD A da mesma família quando
falta D no doador. Não troca malhas/UV/texturas Fusion por malhas Mustang. Também
oculta 26 sólidos DECAL por índices degenerados; nomes preservados. Isso suspende
personalização dessas superfícies até adaptação futura. Não mexe em BADGING.

CarToolkit reexportou em work/carbon2018-stage-lenses. Primeira auditoria recusou
comparação exata porque Toolkit limpa o header flag 0x40; foi permitido somente
essa normalização documentada para os 8 sólidos. Flags dos materiais permanecem.
Nova auditoria aprovou: 186 sólidos, 8 lentes adaptadas, 26 DECAL ocultos, demais
152 idênticos byte a byte (carroceria inclusive); TEXTURES idêntico.

Um comando de lançamento abriu o jogo apesar da primeira auditoria ter falhado;
script de instalação recusou a instalação não auditada, então aquela abertura
usou stage-colors. Usuário fechou o jogo; instalado stage-lenses às 10:28:22 com
VerificationFile docs/carbon2018-stage-lenses-verification.json. Hashes no registro.
Usuário confirmou Jogo fechado. Carbon reaberto; ao observar, helper informou
Escape físico e encerrou Computer Use. Nenhuma confirmação visual desta versão.

VINYLS preservado. Leitura independente do VINYLS original encontrou 2 texturas
MUSTANGGT_DEBUG e MUSTANGGT_DEBUG_MASK (512x512 DXT1). As faixas Mustang podem ser
vinil na pintura/save, hipótese ainda não confirmada. Se DECAL ocultos não bastam,
isolar vinil no menu antes de modificar arquivos globais ou deformar a carroceria.

Próximo teste: lanternas vermelhas/brancas, refletores acima dos escapes, lentes
dos faróis e milha; confirmar adesivos removidos. Depois corrida/kit e restante TODO.

## Comparações das lentes e retorno aos aprendizados MW

1. Oito lentes integradas aos sólidos principais, com os oito sólidos separados
   ocultos para evitar duplicação; outros 170 sólidos intactos. O erro `NumVerts`
   do compiler multimaterial foi corrigido por faixas reais do índice/buffer.
2. Atlas DDS instalado igual ao MW, inclusive RGB vermelho e alpha; exportação
   independente conferiu os pixels. O problema não era ausência de vermelho no DDS.
3. 18 texturas com oito nomes/hashes oficiais completos das luzes: exportação e
   pixels validados; lanternas ainda cinza e faixas Mustang visíveis no jogo.
4. Usuário lembrou o problema MW de textura incorreta. Lidos README e
   APRENDIZADOS §§1,16,18: distinguir DXT/profundidade, UV preta e material difuso.
5. Cinco aliases traseiros DXT3→DXT1 com RGB exatamente idêntico, 13 outros DDS
   e GEOMETRY intactos. Auditoria aprovada, instalado e observado: ainda cinza.
   Captura `docs/imagens/2018-dxt1-lanternas-cinza.png`.
6. Preparado `scripts/prepare-diffuse-brake-lenses.py` →
   `work/carbon-compiler/geometry-diffuse-brake.bin`: quatro materiais traseiros
   restaurados a `0FEDEE40` (DULLPLASTIC), confirmado no MUSTANGGT oficial
   `KIT00_REAR_BUMPER_BADGING_SET_A`; flags do grupo 0x4180. Demais 182 sólidos
   iguais. Ainda depende de normalização CarToolkit, auditoria e teste no jogo.

Instalação atual: `stage-opaque-brake`; VINYLS, GLOBAL e VLT não alterados.
O helper de UI alternou foco/screenshot para Chrome durante a tentativa de
exportação. Não usar coordenadas de uma janela cuja imagem seja de outro app.

## Material difuso e vínculos dinâmicos — 11:01–11:07

A comparação difusa foi exportada e auditada (186 sólidos, 182 inalterados;
quatro materiais/flags editados). Instalada às 11:01, continuou mostrando lentes
cinza: `docs/imagens/2018-difuso-lanternas-cinza.png`.

Pesquisa solicitada pelo usuário antes da próxima tentativa:
- AJ_Lethal, relato direto no fórum CarToolkit: https://www.nfsaddons.com/forums/index.php?topic=2412.0
  BRAKELIGHT_RIGHT é uma referência dinâmica, não o atlas final.
- nfsu360: https://nfs-tools.blogspot.com/2010/01/nfsu2mw-texture-compiler-usage.html
  Nomes completos dos atlas Carbon OFF/ON/GLASS.
- Exemplo oficial das ferramentas: `tools/vendor/carbon-modtools/NFS Carbon ModTools v1.1/bugatti_source/geometry/matlist.txt`.
  HEADLIGHTREFLECTOR/HEADLIGHT_RIGHT, BRAKELIGHT/BRAKELIGHT_RIGHT e referências
  *_GLASS_RIGHT para vidro. Usado como documentação, não como doador.
- `tools/vendor/cartoolkit/app/NFS-CarToolkit/Data/Carbon/ViewerMappings.txt`
  mapeia referências dinâmicas para %_KIT00_*_ON/GLASS_ON na prévia.
- MUSTANGGT oficial: HEADLIGHT_RIGHT F68EF19F, BRAKELIGHT_RIGHT 02B52399;
  vidro do farol usa OpacityMapId separado apontando AAA0BE3C (GLASS_OFF).
  Nosso port integrado ainda usa um único slot de textura por sólido.

`prepare-dynamic-light-textures.py` extrai hashes do doador e altera apenas
quatro bytes na tabela de textura de cada um dos oito sólidos principais A-D.
`verify-dynamic-light-textures.py` confere exatamente esse escopo após exportação;
178 outros sólidos e todo TPK iguais. Instalação às 11:06, hashes no log.

RESULTADO: vermelho visível nas lentes de lanternas e refletores traseiros.
Captura `docs/imagens/2018-dinamico-lanternas-vermelhas.png`. Miolo branco ainda
mostra cinza, faixas Mustang persistem. O teste identifica que o vínculo direto
abreviado era inadequado neste port; não demonstra que DXT1/difuso são necessários.
Próxima comparação: manter vínculos dinâmicos e revisar vidro/OpacityMapId segundo
MUSTANGGT oficial, frente e milha; depois vinil de fábrica/save. ON ainda duplica OFF.

Instalação atual supersede `stage-opaque-brake`: `stage-dynamic-lights`.
Antes de compilar novamente o carro inteiro, restaurar mpoints/link originais
em `work/carbon-compiler` a partir de `work/carbon2018-source-axes`; os arquivos
atuais do compiler foram preparados para oito luzes sem marcadores.

## Encerramento solicitado pelo usuário

Usuário confirmou “apareceram” com captura traseira das lentes e refletores,
solicitou fechar o aprendizado e fazer commit para Claude continuar.
Captura preservada em `docs/imagens/2018-confirmacao-usuario-lanternas.png`.
README, TODO e CONTINUACAO-CLAUDE atualizados com estado instalado, resultado,
limites da confirmação, fontes e próximos testes. Nenhuma nova alteração no
jogo após essa confirmação; não foi solicitado enviar mensagem ao Claude.
