# Sessão Claude — 07/10/2026, 11:17–11:55

Retomada a partir de `docs/CONTINUACAO-CLAUDE.md` (estado `stage-dynamic-lights`).
Todos os testes foram feitos pelo usuário no jogo; instalações com as mesmas checagens
de `scripts/test-install-2018.ps1` (backup `MUSTANGGT_backup_stock` conferido, VINYLS intacto).

## Regravar GEOMETRY.BIN sem CarToolkit

- `scripts/jdlz.py`: porte do JDLZ de OpenNFSTools. A descompressão bate com os 186
  blocos do CarToolkit. `compress` é o guloso de referência (~1,7% maior que o CarToolkit);
  `compress_optimal` (programação dinâmica, literal 9 bits, match 18 bits) fica menor que o CarToolkit.
- Layout do CarToolkit: chunk raiz 0x80134000 → chunk 0 vazio, 0x80134001
  {0x134002 (144 B, contador de sólidos no +12), 0x134003 (hash,0 ordenado),
  0x134004 (hash, offset, packed, unpacked, 0x200, 0)}; blocos 0x55441122+JDLZ
  alinhados a 128 com padding de chunk id 0 (≥ 8 bytes); fim alinhado a 128.
- **Limite de tamanho:** a versão só-aerofólios com o compressor guloso (+29 KB) travou
  ao visualizar o carro; a mesma, com `compress_optimal` (arquivo 4,6 KB menor que o
  anterior), abriu. O Fusion já ocupa ~31,9 MB contra 22 MB do Mustang. Manter o
  GEOMETRY.BIN no máximo do tamanho do último aprovado.

## Lanternas e refletores escuros

O grupo externo da lente (`KIT00_RIGHT_BRAKELIGHT_A..D`, material 1) estava em
DULLPLASTIC/0x4180 desde o teste `diffuse-brake`. Resultado:
- `BRAKELIGHTGLASS`/0x14180 + `BRAKELIGHT_RIGHT` (02B52399): **travou**. No MUSTANGGT
  oficial, BRAKELIGHTGLASS só aparece com `BRAKELIGHT_GLASS_RIGHT` (01F40B32).
- `BRAKELIGHT`/0x4180 + `BRAKELIGHT_RIGHT`: **aprovado** (par oficial do corpo da lanterna).
- Correção de nomes: `F68EF19F` é `HEADLIGHT_GLASS_RIGHT`; `A532FC46` é `HEADLIGHT_RIGHT`.
Script: `scripts/prepare-glass-brake-lenses.py` (`LENS_VARIANT`).

## Aerofólios e entrada de ar do teto

Medição com os modelos do jogo (`CARS/SPOILER`, sem compressão; `CARS/SPOILER_AS2`):
pés a ~2 cm (SPOILER) e 8–9 cm (SPOILER2, herdado do ducktail do Mustang) acima da tampa.
`SPOILER` −2,3 cm e `SPOILER2` −8,7 cm: **aprovado**.

O ROOF_SCOOP só existe em `KIT00_ROOF`, ausente no Fusion. Acrescentar `KIT00_ROOF_A..D`
oculto (clonado do oficial, índices zerados) travou o jogo — mas a mesma build tinha o
compressor guloso, então a causa não está isolada (tamanho ou falta de `ROOF_T0/T1`).
Próximo: `ROOF_MODE=roof+as python scripts/prepare-spoiler-roof.py` (já usa `compress_optimal`),
conferindo antes se o arquivo não ficou maior que o aprovado; vale também testar
`ROOF_MODE=roof`, agora com compressão ótima.

## Release v0.1

`scripts/package_release.py v0.1 local/release-v0.1` → `Fusion2018_AWD_NFSC.zip`
(BIN aprovados: GEOMETRY `AE4BB255…`, TEXTURES `8989A7E4…`), `SHA256SUMS.txt`,
`SHA256SUMS-conteudo.txt`. Instalador com backup em `CARS\MUSTANGGT_original` e
`desinstalar.bat` em `release/pacote/`. Notas: `release/notes-v0.1.md`.
