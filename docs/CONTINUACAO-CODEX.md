# Passagem para o Codex — integração AWD do 2018 (07/10/2026)

## Prioridade atual — substitui os próximos passos históricos abaixo

O usuário considera o visual 2018 finalizado. Escolheu **AWD** e **preço original
Carbon 50.000**. Não retomar testes antigos de lentes/teto já aprovados.

Instalado para teste: **somente GLOBAL/attributes.bin** com acerto MW v2.8
convertido por nomes de campos. SHA-256
`9DECD6C74E3E182468AE625C975213C2C6D311C6978D22086AB2783367899F1C`.
Base e transmissão `_top` usam TORQUE_SPLIT 0,5 e diferencial central 0,75.
Massa 1600, motor/chassi/pneus/freios da referência MW; montagem ecar, altura
visual, áudio/indução/nitro, preço e desbloqueio Carbon preservados.
**Primeiro teste: carregou, condução geral boa, difícil virar mesmo em baixa velocidade.**
Comparação instalada: STEERING 1,1 e STEERING_RANGE +15%, base/upgrades; resto
igual. Nome Fusion também instalado. Nova confirmação solicitada; pendente.
GEOMETRY/TEXTURES são os da v1.1. Release v1.1 publicada é só visual, sem esse acerto.

Backup GLOBAL: `work/global-before-integration-2018`; attributes original
`D64234661F8226FE24ABD45EAE7F5C24CE400A214526A4D23D6B421E75D820E4`.
Instalar/restaurar: `scripts/test-install-performance-2018.ps1 -Action Install/Restore`
(jogo e VltEd fechados). Scripts distribuíveis e rollback em `release/vlt`.
Auditoria: 10.180 nós e 312 blobs; só 11 nós/76 campos alterados; CAMARO/CAMARON
e demais nós intactos; rollback semanticamente idêntico.
Relatórios `docs/carbon2018-performance-plan.json` e `*-verification.json`.

**Corrigir o inventário inicial:** existem níveis `mustanggt_top` e coleções de
indução próprias. `vlt_dump.py` não resolvia nomes; usar o dump completo
`work/vlt-baseline-yaml`. Attribulator v2.0 em
`tools/vendor/attribulator/v2/release_windows`, obtido da release oficial:
https://github.com/NFSTools/Attribulator/releases/download/v2.0.0/release_windows.zip
SHA-256 `3D4D15677C6625EB37EBCEBE0D07BD1322D53F632B0CE7D05F1461E183218C95`.
`unpack -i <GLOBAL> -o <dump> -p CARBON -f yml`; gerar scripts com
`prepare-performance-2018.py`; aplicar com `apply-script-bin`.
A saída compilada fica na subpasta **main**. Extrair candidata/rollback para
`work/vlt-performance-yaml`/`work/vlt-rollback-yaml` e rodar
`verify-performance-2018.py` antes de instalar.

**Nome preparado e instalado para teste:** `prepare-frontend-name-2018.py` gerou 17
arquivos em `work/languages2018-name`; backup `work/languages-before-integration-2018`.
CARNAME_FORD_MUSTANGGT (1CC69F99) → Ford Fusion Titanium AWD; todos os outros textos,
chunks e charset intactos. Auditoria `docs/carbon2018-frontend-name-verification.json`.
Com NFSC fechado, `test-install-frontend-name-2018.ps1 -Action Install`; Restore
recupera idiomas originais. Validar nome no jogo depois da instalação.

Próximos: resposta do teste de direção e nome; adaptar logotipo Fusion;
depois Fusion 2012 FWD → **CAMARO oficial**, preservando CAMARON. ON de freio e
faixas de fábrica continuam melhorias pendentes. Ao parar, documentar e fazer
commit com coautoria. Push/release ficam com o usuário.

---

## Histórico: teto e JDLZ

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
