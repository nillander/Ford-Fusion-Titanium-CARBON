# Passagem para Claude — 07/10/2026 às 02:31

Retomada informada pelo usuário, America/Sao_Paulo. Este documento não agenda a sessão.
Assumir TODO.md; ao parar, atualizar os registros e fazer commit com coautoria do agente.
Trabalhar em pt-BR. Usar exclusivamente os veículos oficiais que serão substituídos
como doadores: CAMARO → Fusion 2012 FWD, MUSTANGGT → Fusion 2018. Preservar CAMARON.
As cópias instaladas ainda têm origem vanilla não comprovada; confirmar antes de tratá-las
como oficiais. Não substituir por outro carro/mod.

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
