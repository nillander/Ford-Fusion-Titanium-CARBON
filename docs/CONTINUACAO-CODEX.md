# Passagem para o Codex — teste do teto e JDLZ (07/10/2026)

## Atualização prioritária: teste instalado

`work/carbon2018-stage-roof` instalado; GEOMETRY SHA-256
`DE8EE10F8DDA430076D15CAD4DA796398B5BC85DC2EC9D33B4B6B1F94967680E`.
TEXTURES permanece `8989A7E4…`; VINYLS/GLOBAL/VLT/CAMARO intactos.
Gate: `docs/carbon2018-stage-roof-verification.json`. São 190 sólidos, com todas
as 186 peças da v1.0 idênticas após descompressão e quatro ROOF nativos do nfscgc.
O usuário confirmou que carregou e as entradas comum/AutoSculpt aparecem:
“teto resolvido”. Correção aprovada no jogo; candidata à próxima release.

**Revisão das conclusões históricas abaixo:** a recompilação também travou antes
de corrigir JDLZ. Seis dumps apontam para o descompressor, que exige flags no fim
do último grupo. O compressor antigo removia essas flags; o leitor independente
parava na saída e não detectava isso. `jdlz.py` corrigido e regressões aprovadas.
Não afirmar que inserir peças ou crescer o arquivo é a causa desses crashes.

Reprodução: `prepare-roof-compiler-source.py`; compilar BASE_A.obj da pasta
`work/carbon2018-source-roof` no nfscgc; inventariar/extrair a saída;
`consolidate-roof-compile.py prepare`; CarToolkit abre
`work/carbon-compiler/geometry-roof-consolidated.bin` e exporta Carbon/Racer/MUSTANGGT
para `work/carbon2018-roof-normalized`; `consolidate-roof-compile.py finish`;
inventário/extrator/leitor independente. A consolidação usa as peças aprovadas
para preservar todas as correções anteriores e normaliza os fins de streams.

Para voltar à v1.0, fechar NFSC e instalar com o gate
`docs/carbon2018-stage-spoiler-verification.json` (não usar Restore, que volta stock).

## Passagem anterior — v1.0, 12:40 (histórico)

Trabalhar em pt-BR. Ao parar: atualizar TODO/README, registrar a sessão em
`docs/SESSAO-CODEX-<data>.md` e fazer commit com coautoria. Push, tags e releases
ficam com o usuário (Cursor). Fechar o jogo antes de qualquer instalação.

## Estado atual

- **Publicado:** release **v1.0** no GitHub (tag `v1.0` → `e1df347`; `main` em `8b832d3`).
  Fusion 2018 no slot `MUSTANGGT`. Pacote local em `local/release-v0.1/`
  (nome antigo da pasta; conteúdo é o da v1.0).
- **Instalado no jogo = release v1.0:**
  GEOMETRY `AE4BB255576689D0668AAB54B677F8D3393AE74C5A15700AB2176FDC89B647B2`,
  TEXTURES `8989A7E4502F92B2D2828E817AD8B7F3ACB0D46A4227B6275CA013EA3651E3AC`,
  VINYLS original. Staging de origem: `work/carbon2018-stage-spoiler`
  (`docs/carbon2018-stage-spoiler-verification.json`). GLOBAL, VLT e CAMARO intactos.
- **Aprovado pelo usuário no jogo:** carroceria, rodas, faróis, farol de milha,
  lanternas e refletores traseiros, aerofólios da loja (comuns e AutoSculpt).
- **Backup do Mustang original:** `CARS/MUSTANGGT_backup_stock` (confere com
  `reference/carbon-stock/MUSTANGGT`).
- **Instalar/restaurar:** `scripts/test-install-2018.ps1 -Action Install
  -VerificationFile docs/carbon2018-stage-spoiler-verification.json` reinstala a v1.0;
  `-Action Restore` volta ao Mustang original. Atenção: sem `-VerificationFile` o
  script usa `stage-axes`, que é antigo.

## O que não fazer (aprendido em 07/10)

1. **Não acrescentar sólidos a um GEOMETRY.BIN pronto.** Três tentativas de pôr
   `KIT00_ROOF` para a entrada de ar travaram o jogo ao visualizar o carro: clones EA
   do Mustang (só ROOF_A..D; depois com ROOF_T0/T1, vértices zerados e arquivo 33 KB
   menor que a v1.0) e clones no formato CarToolkit a partir dos placeholders
   `KIT00_SPOILER`. Editar sólidos existentes funciona; criar novos, não. O código das
   tentativas está no branch local `experimento/entrada-de-ar-teto` (só consulta).
2. **Não aumentar o GEOMETRY.BIN.** A versão só com aerofólios, comprimida com o JDLZ
   guloso (+29 KB), travou; a mesma com `jdlz.compress_optimal` (menor que a anterior)
   abriu. Manter o arquivo ≤ 31.880.960 bytes (tamanho da v1.0) até entender o limite.
3. **Pares light material × textura dinâmica precisam existir no Mustang oficial.**
   `BRAKELIGHTGLASS` + `BRAKELIGHT_RIGHT` travou. Os que funcionam: `BRAKELIGHT` +
   `BRAKELIGHT_RIGHT` (02B52399) na lanterna; `HEADLIGHTGLASS` + `HEADLIGHT_GLASS_RIGHT`
   (F68EF19F) no farol. Atenção: F68EF19F é **HEADLIGHT_GLASS_RIGHT**; HEADLIGHT_RIGHT é A532FC46.
4. Sólidos oficiais (formato EA: flag 0x40, um buffer por material, chunks 0x134C02 e
   0x13401D) não se misturam com os do CarToolkit (flag 0, um buffer).

## Ferramentas sem GUI disponíveis

- `scripts/jdlz.py`: `decompress`, `compress` (guloso) e `compress_optimal` (menor que o
  CarToolkit). Cache de recompressão: `scripts/recompress_cache.py` → `work/jdlz-cache`.
- Remontagem de GEOMETRY.BIN no layout CarToolkit (cabeçalho 0x134002/3/4, blocos
  0x55441122 alinhados a 128): ver `scripts/prepare-spoiler-roof.py` (modo `none`,
  usado na v1.0) e `scripts/prepare-glass-brake-lenses.py`.
- Leitores: `scripts/vlt_dump.py` (VPAK/VLT, só leitura), `scripts/dump_position_markers.py`.
- Detalhes técnicos: `docs/SESSAO-CLAUDE-2026-10-07-tarde.md`.

## Próximos passos, em ordem

1. **Nome, logotipo, preço e fabricante no frontend (VltEd 4.6).** Backup de
   `GLOBAL/attributes.bin` e `GLOBAL/FE_ATTRIB.bin` antes. `frontend/mustanggt` já herda
   de `ford`. Nome "Ford Fusion Titanium AWD" (ver `FE.MWPS` da v2.8 MW). Coleções em
   `docs/vlt-slots.json`.
2. **Performance e tração do 2018.** Perguntar ao usuário: RWD (como na v2.8 MW) ou AWD
   real. Converter a intenção do `ATTRIBUTES.MWPS` MW para os nós `mustanggt`
   (engine, transmission, chassis, tires, brakes). MUSTANGGT não tem induction/nos próprios.
3. **Luz de freio acesa.** Hoje o atlas ON é cópia do OFF. Gerar `KIT00_BRAKELIGHT_ON`
   (7E68A778) mais claro na área da lente (u 0,669–0,996, v 0,033–0,361; vermelho médio
   atual 97/255) e reexportar o TPK no CarToolkit. Só textura; GEOMETRY intacto.
4. **Faixas/adesivos do Mustang fora do lugar.** Os 26 DECAL ocultos não resolveram.
   Investigar vinil de fábrica/preset e `VINYLS.BIN` (texturas MUSTANGGT_DEBUG*) antes de
   mexer em arquivos globais.
5. **Entrada de ar do teto.** Único caminho que resta: recompilar o carro inteiro no
   nfscgc com uma peça `KIT00_ROOF_A..D` na fonte (OBJ mínimo oculto dentro do teto) e
   `_ROOF_SCOOP00` no `mpoints.txt` (posição Fusion: x 0,10, z 1,2376, inclinação 5,35°;
   ver `scripts/prepare-roof-scoop.py` no branch experimental). Depois reaplicar, em
   ordem, as correções da v1.0: matrizes dos marcadores do doador, cores de vértice,
   lentes, vínculos dinâmicos, lente `BRAKELIGHT`, alturas dos aerofólios (SPOILER −0,023,
   SPOILER2 −0,087). Consolidar isso num único script antes. Arquivo final ≤ v1.0.
6. **Fusion 2012 → CAMARO** (FWD, fabricante Ford no FE, preservar `CAMARON`, que herda
   `pvehicle/camaro`). Reaproveitar a cadeia do 2018 desde a compilação com eixos corrigidos.
7. Cada etapa aprovada pelo usuário no jogo vira candidata à próxima release (v1.1).
