# Passagem para o Codex — 07/10/2026, manhã

> **Estado mais recente — 11:06:** instalado `stage-dynamic-lights`.
> Vermelho visível nas lanternas e refletores após usar HEADLIGHT_RIGHT e
> BRAKELIGHT_RIGHT do MUSTANGGT oficial. DXT1 isolado e difuso isolado não
> corrigiram. Miolo branco/partes cinza, frente, milha, luzes ON e adesivos
> Mustang ainda pendentes. Ler o fim do README e da sessão Codex; os estados
> anteriores abaixo são histórico. GEOMETRY `8158464702D4B7805844C60E392121ABF72356E41AC4AA905725578CEC2FB4EE`;
> TEXTURES `8989A7E4502F92B2D2828E817AD8B7F3ACB0D46A4227B6275CA013EA3651E3AC`.

> **Atualização após execução pelo Codex:** recompilação e auditoria concluídas;
> instalação experimental ativa e Fusion 2018 com rodas observado no jogo.
> Ler `docs/SESSAO-CODEX-2026-10-07.md` e o TODO atualizado para o estado atual.
> **10:18, continuação:** `stage-colors` instalado com 552 cores recuperadas;
> faixas/artefatos persistem. Usuário interrompeu Computer Use com Esc. Fechar
> o jogo antes de nova instalação; corrida e kits ainda não testados.
> **10:28:** `stage-lenses` instalado. Usuário considera carroceria boa; faltam
> lentes de lanternas/refletores/faróis/milha e adesivos Mustang estão deslocados.
> Oito configurações de lentes do doador recuperadas e 26 DECAL ocultos, com
> 152 sólidos intactos. Confirmar resultado visual; Computer Use interrompido
> com Esc antes da observação. VINYLS não mudou e pode explicar faixas persistentes.
> Os passos abaixo registram a passagem original. Próximo trabalho: artefatos
> visuais e compatibilidade de peças; o primeiro teste não aprova a release.

Trabalhar em pt-BR. Ler antes: `TODO.md` (estado consolidado), `docs/SESSAO-CLAUDE-2026-10-07.md`.
Ao parar, atualizar TODO/README e fazer commit com coautoria.

## Por que o usuário não viu nada no jogo

Nada foi instalado. `CARS/MUSTANGGT` e `CARS/CAMARO` no jogo continuam com os BIN
originais (mtime 2006-10-14, SHA-256 iguais a `reference/carbon-stock/`). O staging
`work/carbon2018-stage` **não deve ser instalado**: está girado 90° e sem pontos de
montagem. O objetivo desta sessão é chegar ao **primeiro teste visível em jogo** do
Fusion 2018 no slot MUSTANGGT, de forma reversível.

## O que a sessão Claude deixou pronto (commit b831d70)

| Item | Onde |
| --- | --- |
| Causa da rotação: nfscgc grava (x′,y′)=(y,−x) | `docs/SESSAO-CLAUDE-2026-10-07.md` §1 |
| Fonte pré-girada (−y, x, z) + 165 OBJ de ponto de montagem + `mpoints.txt` | `work/carbon2018-source-axes/` (gerada por `scripts/prepare-compiler-input.py`) |
| Relatório dos pontos (posição Carbon, peça, rotação) | `docs/carbon2018-mountpoints.json` |
| Marcadores do doador e do MW | `docs/{mustanggt,camaro}-stock-markers.json`, `docs/mw20{12,18}-markers.json` |
| Leitor de marcadores (chunk 0x13401A; padding 0x11) | `scripts/dump_position_markers.py`, `scripts/mw_position_markers.py` |
| Leitor VPAK/VLT somente leitura | `scripts/vlt_dump.py`; resumo `docs/vlt-slots.json` |
| VltEd 4.6 extraído | `tools/vendor/cartoolkit/vlted/NFS-VltEd.exe` |

A pasta `work/` é ignorada pelo Git. Se faltar `work/carbon2018-source-axes`, regenerar com
`python scripts/prepare-compiler-input.py` (lê `work/carbon2018-source` e `docs/mw2018-markers.json`).

## Passo 1 — Recompilar com a fonte corrigida (GUI)

1. `work/carbon-compiler/nfscgc.exe`, working directory nessa pasta. XNAME `MUSTANGGT`.
   Selecionar **todos** os `.obj` de `work/carbon2018-source-axes` (186 peças + 165 pontos).
2. Conferir onde o nfscgc procura `mpoints.txt`/`link.txt`/`matlist.txt`: o binário
   imprime `Loading mpoints.txt...Loaded/Failed`. Se carregar da pasta do executável,
   copiar os três arquivos de `work/carbon2018-source-axes` para `work/carbon-compiler/`
   (guardar os anteriores).
3. No log: esperar `Mount point processed` e nenhum `Not found any part for the mount point`
   nem `Mount point skipped`. Se os OBJ de ponto virarem sólidos na saída
   (`MUSTANGGT_LEFT_HEADLIGHT00` etc.), registrar; não é o esperado.
4. CarToolkit 3.1: abrir a saída, Carbon/Racer/MUSTANGGT, exportar para
   `work/carbon2018-stage-axes/GEOMETRY.BIN`. Texturas: reaproveitar
   `work/carbon2018-stage/TEXTURES.BIN` (não depende da orientação) ou reexportar igual antes.

## Passo 2 — Auditoria obrigatória antes de instalar

```powershell
pwsh -NoProfile -File scripts/extract-carbon-solids.ps1 -InventoryFile <inventário novo> -OutputRoot work/carbon2018-stage-axes-solids
pwsh -NoProfile -File scripts/validate-carbon-solids.ps1 -InputRoot work/carbon2018-stage-axes-solids -OutputFile docs/carbon2018-stage-axes-audit.json
python scripts/dump_position_markers.py work/carbon2018-stage-axes-solids docs/carbon2018-stage-axes-audit.json docs/carbon2018-stage-axes-markers.json
```
(regenerar o inventário com `inventory(path, carbon=True, extracted_root=...)` de `scripts/inventory_geometry.py`, como na passagem anterior)

Critérios de aprovação:
- `KIT00_BODY_A`: X ≈ −2,36 → 2,37 (frente em +X), Y ≈ ±1,04, Z ≈ −0,04 → 1,26.
  `KIT00_RIGHT_BRAKELIGHT_GLASS_A` com X negativo (traseira). Pneu com largura em Y.
- Marcadores presentes em `BASE_A..E`, `KITxx_BODY_A..E` e `KIT00_FRONT_TIRE_*`,
  posições iguais às de `docs/carbon2018-mountpoints.json` (tolerância 1 mm).
- Matrizes de rotação dos marcadores compatíveis com as do doador para o mesmo nome
  (`docs/mustanggt-stock-markers.json`; ex. headlight linhas (0,0,1),(0,−1,0),(1,0,0);
  brake/reverse (0,0,1),(0,1,0),(−1,0,0)). Se divergirem, ajustar a coluna de rotação
  do `mpoints.txt` (o compilador pode aplicar a mesma rotação de eixos às rotações) e recompilar.
- Contagens de índices ≤ 65535 e sem sentinel, como na auditoria anterior.

## Passo 3 — Primeiro teste em jogo (reversível)

Só depois do Passo 2 aprovado:
1. Backup: copiar `CARS/MUSTANGGT/` inteira para `CARS/MUSTANGGT_backup_stock/` e conferir
   SHA-256 contra `reference/carbon-stock/MUSTANGGT/` (`55957752…` geometria).
2. Copiar `GEOMETRY.BIN` e `TEXTURES.BIN` de `work/carbon2018-stage-axes/` para `CARS/MUSTANGGT/`.
   Manter o `VINYLS.BIN` original.
3. Teste do usuário: Corrida rápida ou Desafio → escolher o Mustang GT. Se o carro sumir ou
   faltarem peças, é a lacuna de kits/peças do doador (Fusion não tem `ROOF`,
   `FRONT/REAR_BUMPER`, `LEFT_HEADLIGHT`, `LEFT_BRAKELIGHT` como peças separadas);
   anotar o que falta e ir para o mapa de peças (`docs/mustanggt-part-map.csv`).
4. Reverter: copiar de volta os BIN de `CARS/MUSTANGGT_backup_stock/`.
   Nada de VLT/FE neste teste: o nome continua "Mustang GT".

Atenção: o jogo tem NFSCUnlimiter (`MissingPartsFix=1`, `ReplacementModel=1`/CARRERAGT).
Um carro inválido pode ser trocado pelo Carrera GT em vez de travar.

## Depois do primeiro teste

- Lacunas de peças exigidas pelo slot (kits KIT01–05/KITW, para-choques, teto, damage,
  AutoSculpt `_T0/_T1`). Pontos ainda sem fonte: `LICENSEPLATE`, `ROOF_SCOOP`,
  `LEFT/RIGHT_EXHAUST` dos para-choques, hashes 0x45D8B27B/C, 0x7C883442/3, 0x357E917F, 0xD1409DEE.
- VltEd (sempre com backup de `GLOBAL/attributes.bin` e `FE_ATTRIB.bin`): nome FE,
  fabricante Ford no `camaro`, FWD em `transmission/camaro`. `pvehicle/camaron` herda de
  `pvehicle/camaro`: conferir valores efetivos do CAMARON antes e depois.
- Decisão pendente do usuário: 2018 RWD (como no MW) ou AWD real.
- 2012 → CAMARO: repetir a cadeia com `scripts/prepare-compiler-input.py` adaptado
  (fonte COBALTSS, `docs/mw2012-markers.json`, doador `docs/camaro-stock-markers.json`, XNAME `CAMARO`).
