# Passagem para Claude — atualização de 07/10/2026, 11:07

> **Atualização 07/10 11:55 (Claude):** instalado e aprovado `stage-spoiler`
> (GEOMETRY `AE4BB255…`): lanternas/refletores corretos e aerofólios assentados.
> Release v0.1 preparada. Leia [SESSAO-CLAUDE-2026-10-07-tarde.md](SESSAO-CLAUDE-2026-10-07-tarde.md)
> antes de regravar BIN (limite de tamanho; pares light material × textura dinâmica).

## Estado atual confirmado pelo usuário

O Fusion 2018 aparece no Carbon. A carroceria foi considerada boa pelo usuário.
Em `stage-dynamic-lights`, as lentes vermelhas das lanternas e os refletores acima
dos escapamentos apareceram; o usuário confirmou com captura e pediu o commit
para você continuar. As faixas Mustang deslocadas persistem e o miolo das
lanternas ainda mostra elementos cinza. Não tratar como release aprovada.

Instalação atual, somente MUSTANGGT GEOMETRY/TEXTURES:

- GEOMETRY SHA-256: `8158464702D4B7805844C60E392121ABF72356E41AC4AA905725578CEC2FB4EE`
- TEXTURES SHA-256: `8989A7E4502F92B2D2828E817AD8B7F3ACB0D46A4227B6275CA013EA3651E3AC`
- Staging: `work/carbon2018-stage-dynamic-lights`.
- Auditoria/gate: `docs/carbon2018-stage-dynamic-lights-verification.json`.
- VINYLS, GLOBAL e VLT permanecem anteriores; o carro ainda se chama Mustang e
  usa a performance do slot. Fusion 2012 ainda não foi portado.

### Aprendizado que resolveu o aparecimento

O port referenciava diretamente os atlas abreviados HEAD_OFF/BRAKE_OFF. Os DDS
tinham os pixels corretos, mas o jogo não os exibia nas lentes. Nomes completos
no TPK, DXT1 isolado e material difuso isolado não resolveram.
Oito referências de textura nos sólidos principais A–D foram então trocadas
pelos hashes dinâmicos do MUSTANGGT oficial: `HEADLIGHT_RIGHT` (`F68EF19F`) e
`BRAKELIGHT_RIGHT` (`02B52399`). Só esses oito hashes mudaram no último teste;
178 sólidos e todas as texturas ficaram idênticos. O vermelho apareceu.
As fontes da pesquisa e capturas estão no fim do README e da sessão Codex.

### Próximos passos

1. Conferir faróis/milha, lente branca da lanterna e transparência; preservar
   cobertura externa. O vidro do farol oficial possui diffuse dinâmico e
   OpacityMapId separado para GLASS_OFF, enquanto a integração atual usa uma
   única entrada de textura. Comparar essa estrutura antes de novas mudanças.
2. Manter o vínculo dinâmico e comparar DXT3/material de vidro reversivelmente:
   o último teste ainda herda DXT1 traseiro + difuso. Não concluir que ambos
   são necessários só porque a combinação final apareceu.
3. Corrigir estados ON: os oito aliases atuais copiam os atlas OFF. Fazer QA
   em corrida, freio, ré, faróis e LODs/kits antes de aprovar iluminação.
4. Resolver faixas Mustang via vinil de fábrica/save/UV. Ocultar 26 sólidos
   DECAL não removeu as faixas; VINYLS continua stock. Não apagar emblemas Fusion.
5. Seguir TODO para kits, VLT/FE e Fusion 2012 no CAMARO, preservando CAMARON.

Para recriar aliases: `scripts/prepare-light-texture-aliases.py`; importar a pasta
resultante no CarToolkit e exportar Carbon com
`source/Fusion2018_Carbon_LightTextures.txt`. O limite de 23 caracteres do mwtc
não é regra geral do Carbon; manter nomes/hashes oficiais completos das luzes.
Antes de compilar o carro inteiro, restaurar mpoints/link de
`work/carbon2018-source-axes` no cwd do compiler: os atuais são do teste só de luzes.
Fechar NFSC antes de instalar; usar gate específico em `test-install-2018.ps1`.
Reversão stock: `scripts/test-install-2018.ps1 -Action Restore` com o jogo fechado.

## Passagem original — 02:31 (histórico; supersedida pelo estado acima)

Retomada informada pelo usuário, America/Sao_Paulo. Este documento não agenda a sessão.
Assumir TODO.md; ao parar, atualizar os registros e fazer commit com coautoria do agente.
Trabalhar em pt-BR. Usar exclusivamente os veículos oficiais que serão substituídos
como doadores: CAMARO → Fusion 2012 FWD, MUSTANGGT → Fusion 2018. Preservar CAMARON.
As cópias instaladas ainda têm origem vanilla não comprovada; confirmar antes de tratá-las
como oficiais. Não substituir por outro carro/mod.

> **Atualização 07/10 (Claude):** o staging 2018 saiu **girado 90°** pelo nfscgc e
> não tinha nenhum ponto de montagem. Fonte corrigida e `mpoints.txt` em
> `work/carbon2018-source-axes`. Detalhes e próximos passos em
> [SESSAO-CLAUDE-2026-10-07.md](SESSAO-CLAUDE-2026-10-07.md).

## Estado entregue

- Referências v2.8 verificadas, backup CARS/GLOBAL e manifesto de 73 arquivos.
- 848 sólidos CAMARO + 997 MUSTANGGT descomprimidos CIP (HUFF/JDLZ), com limites,
  cobertura, tamanho e hashes conferidos. Leitor independente validou índices,
  posições e UVs das 1845 malhas; 269 possuem morph targets.
- Fusion 2018: 186 sólidos, 86 nomes exatos do doador. Há 911 nomes do doador sem
  correspondência exata: esse número não define quantas peças são obrigatórias.
- CarToolkit 3.1 e ModTools 1.1 obtidos e operados. VltEd 4.6 baixado, ainda no 7z.
- Erro de índices resolvido em staging: 13 malhas acima de 65535 índices (BASE_A,
  seis KITxx_BODY_A e seis KITxx_BODY_B) simplificadas por material; máximo 65397.
- ModTools compilou os 186 OBJ, mas a saída bruta tem um sólido vazio hash zero e
  contagens de vértices de materiais incompatíveis com o leitor independente.
  NÃO instalar work/carbon-compiler/geometry.bin.
- CarToolkit reconheceu 186 sólidos reais na saída bruta e reexportou para Carbon:
  work/carbon2018-stage/GEOMETRY.BIN. Todos passaram no leitor independente,
  sem sentinel, depois da descompressão.
- work/carbon2018-stage/TEXTURES.BIN: 10 texturas Carbon, nomes ≤23 caracteres,
  hashes únicos, formatos DXT e dados dos mipmaps declarados validados.
  As fontes atuais declaram apenas um nível; isso não certifica qualidade visual.
- Configuração source/Fusion2018_Carbon.txt renomeia luzes para MUSTANGGT_BRAKE_OFF
  e MUSTANGGT_HEAD_OFF, correspondentes aos hashes na geometria.
- Nenhum jogo/VLT alterado, instalação, release ou QA em jogo. 2012 ainda não portado.

## Próximos passos

1. Confirmar origem oficial dos doadores; Backup existente só contém localização.
   Não sobrescrever as referências preservadas com arquivos modificados.
2. Adaptar staging ao MUSTANGGT oficial: pontos de montagem (rodas, escape, spoiler,
   luzes), kits, LODs, cutscenes/IA, damage e AutoSculpt. mpoints.txt é placeholder.
   Não há montagem funcional validada. A saída ainda não é um port instalável.
3. Revisar effects/materiais Carbon e texturas compartilhadas. O exporter preservou
   oito hashes sem nomes como 0xHASH. CarToolkit/Data/Textures.txt identifica
   DUMMY_DECAL1..6 e DUMMY_NUMBER_LEFT/RIGHT; confirmar no GLOBAL Carbon.
   Não assumir que shaders MW com o mesmo hash dão o mesmo visual.
4. QA da redução: meshoptimizer 1.3.0, Sparse/Permissive, pesos normais 0.1 e UVs 1,
   erro alvo 0.01; maior erro relativo ponderado observado ~0.001241 (não metros).
   LockBorder impedia atingir o limite e não foi usado. Vértices e atributos vêm
   do original, mas faces/bordas mudaram: revisar costuras, UVs e silhueta.
   OBJ não preserva cores de vértices do BIN MW.
5. DXT3 em BADGING e SKIN19 ainda exige revisão de alpha/opacos. Considerar mipmaps.
6. Inspecionar VLT real antes de converter MWPS. 2018 está RWD apesar do nome AWD;
   decisão pendente. 2012 exige FWD e confirmação CAMARO inicial.
7. Após compatibilidade estrutural/visual: instalação reversível com backup, QA,
   repetir para 2012 → CAMARO, então release. Não marcar Fases 1–7 completas.

## Reprodução na raiz do projeto

Ferramentas/BIN ignorados pelo Git existem neste computador; origens em tools/README.md.

```powershell
pwsh -NoProfile -File scripts/extract-carbon-solids.ps1
python scripts/inventory_geometry.py
pwsh -NoProfile -File scripts/validate-carbon-solids.ps1
python scripts/prepare-simplification.py
node scripts/simplify-carbon-source.mjs
python scripts/prepare-carbon-source.py --indices-directory work/simplification2018
```

O exporter depende de numpy, parser MW irmão e work/mw2018-textures.json + work/mw2018-dds.
Para recriar metadata/DDS:
```powershell
& 'C:\Program Files\dotnet\dotnet.exe' '..\fusion-mw2005\scripts\validator\bin\Release\net8.0\Validator.dll' 'reference\mw-v28\Fusion2018_AWD_MW2005\Fusion2018_AWD_MW2005\CARS\MUSTANGGT\TEXTURES.BIN' 'work\mw2018-textures.json' 'work\mw2018-dds'
```
Usar C:\Program Files\dotnet\dotnet.exe (x64):
`dotnet` padrão é x86 e não lista SDK. Assembly existente:
C:\Users\nillander\NoDocuments\fusion-mw2005\scripts\validator\bin\Release\net8.0\Validator.dll.

Fonte 2018: reference/mw-v28/Fusion2018_AWD_MW2005/Fusion2018_AWD_MW2005/CARS/MUSTANGGT/.
Fonte 2012: reference/mw-v28/Fusion2012_FWD_MW2005/Fusion2012_FWD_MW2005/CARS/COBALTSS/.
Doadores: reference/carbon-stock/{CAMARO,MUSTANGGT}; backup GLOBAL: reference/carbon-global-before/.

Compilação GUI:
1. work/carbon-compiler/nfscgc.exe, working directory nessa pasta (materiais/mp.txt
   já presentes). MUSTANGGT, Save log, Compile, selecionar OBJ em work/carbon2018-source.
   Os 186 OBJ, matlist/link/mpoints estão preparados. Log append contém falhas antigas
   seguidas do sucesso; olhar o final.
2. CarToolkit: abrir work/carbon-compiler/geometry.bin, Carbon/Racer/MUSTANGGT,
   saída manual work/carbon2018-stage, exportar GEOMETRY.BIN config-free.
3. Texturas: carregar TEXTURES.BIN original MW, Configuration Auto desmarcado →
   source/Fusion2018_Carbon.txt, Carbon/MUSTANGGT, mesma saída, exportar TEXTURES.BIN.

A GUI foi controlada com skill computer-use e @oai/sky. Nas janelas de arquivo,
digitar o caminho no campo Nome: a barra de endereço pode fechar nfscgc. Árvores de
acessibilidade às vezes vêm atrasadas: observar novamente antes de usar índices.

Auditoria da saída existente:
```powershell
pwsh -NoProfile -File scripts/extract-carbon-solids.ps1 -InventoryFile docs/carbon2018-stage-inventory.json -OutputRoot work/carbon2018-stage-solids
pwsh -NoProfile -File scripts/validate-carbon-solids.ps1 -InputRoot work/carbon2018-stage-solids -OutputFile docs/carbon2018-stage-audit.json
pwsh -NoProfile -File scripts/validate-carbon-textures.ps1
```
Ao alterar o BIN, regenerar inventário staging com inventory(path, carbon=True,
extracted_root=work/carbon2018-stage-solids), do script inventory_geometry.py.
O leitor TPK usa Version3Tpk.cs irmão recompilado com nosso decoder CIP; a assembly
MW sozinha rejeita os recursos comprimidos.

## Relatórios

geometry-inventory.json; carbon-mesh-audit.json; mustanggt-part-map.csv;
carbon2018-source-report.json; carbon2018-simplification.json;
carbon2018-compiled-inventory.json (187 entradas brutas, incluindo vazio);
carbon2018-stage-inventory.json; carbon2018-stage-audit.json;
carbon2018-texture-audit.json; carbon2018-stage-verification.json.

Próximo objetivo: adaptação ao doador oficial, antes de instalar o staging atual.
