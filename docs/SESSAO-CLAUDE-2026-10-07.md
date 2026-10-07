# Sessão Claude — 07/10/2026, 02:31–

Retomada automática agendada pelo usuário, a partir da passagem do Codex
(`docs/CONTINUACAO-CLAUDE.md`, commit 2887ff8). Nenhum arquivo do jogo foi alterado.

## 1. Bloqueador encontrado: staging 2018 girado 90°

A auditoria anterior validou índices, UVs e limites, mas não a orientação.
Comparando caixas delimitadoras (`docs/carbon-mesh-audit.json` × `docs/carbon2018-stage-audit.json`):

| Sólido | Doador oficial (min → max) | Staging Fusion (min → max) |
| --- | --- | --- |
| `KIT00_BODY_A` | X −2,17 → 2,29 · Y ±0,94 | X ±1,04 · Y −2,37 → 2,36 |
| `KIT00_RIGHT_BRAKELIGHT_GLASS_A` | X −2,25 → −2,11 (traseira) | Y +1,81 → +2,32 |
| `KIT00_FRONT_TIRE_A` | largura em Y | largura em X |

O cabeçalho do sólido (bounds) também está girado, com matriz pivô identidade: o
carro apareceria de lado no jogo. Os OBJ de entrada (`work/carbon2018-source`)
estão corretos (X frente). A saída bruta do nfscgc
(`work/carbon2018-compiled-solids`) já vem girada, então a causa é o compilador:
ele grava **(x′, y′) = (y, −x)** — espera a frente em +Y e o lado esquerdo em −X.

Correção: `scripts/prepare-compiler-input.py` gera `work/carbon2018-source-axes`
com posições e normais pré-giradas por (x, y, z) → (−y, x, z). É rotação pura
(sem espelhamento), então enrolamento das faces e UVs ficam iguais.
**Não instalar `work/carbon2018-stage`.**

## 2. Pontos de montagem

`scripts/dump_position_markers.py` lê o chunk 0x13401A (80 bytes por marcador;
o preenchimento até 16 bytes usa 0x11). Resultados:

- Doador MUSTANGGT: 296 marcadores em 65 sólidos. CAMARO: 276 em 63.
- Fusion MW v2.8 (`scripts/mw_position_markers.py`): 11 marcadores por LOD de
  `BASE_A..E` (faróis, lanternas, ré, escapes, brake light central, spoiler, roof scoop).
- Staging 2018 atual: **zero** marcadores (o `mpoints.txt` estava vazio).

Diferença de convenção: no doador oficial `LEFT_*` fica em +Y. No Fusion MW, faróis,
lanternas e escapes `LEFT_*` estão em −Y (as luzes de ré seguem +Y). O gerador
renomeia pelo lado real (LEFT = +Y).

O gerador escreve `mpoints.txt` no formato do exemplo do autor (`bugatti_source`)
e um OBJ mínimo por ponto (triângulo de 2 mm centrado na posição), anexado às mesmas
peças que o doador usa: faróis/lanternas/ré/SPOILER/SPOILER2 em `BASE_A..E`;
`EXHAUST` e ré em `KITxx_BODY_A..E`; `FRONT_BRAKE` em `KIT00_FRONT_TIRE_*`.
SPOILER2 = SPOILER + o mesmo deslocamento do doador. Total: 165. Relatório:
`docs/carbon2018-mountpoints.json`.

Ainda sem fonte: `LICENSEPLATE` (MW não tem; Fusion não tem `REAR_BUMPER`),
`ROOF_SCOOP` (Fusion não tem `KIT00_ROOF`), `LEFT/RIGHT_EXHAUST` dos para-choques
KIT01+, e os quatro hashes não resolvidos do teto AutoSculpt (0x45D8B27B/C, 0x7C883442/3)
e de `KIT00_ROOF` (0x357E917F, 0xD1409DEE). As rotações vêm do exemplo do autor
e precisam ser conferidas contra as matrizes do doador após compilar.

## 3. VLT (somente leitura)

`attributes.bin`, `FE_ATTRIB.bin` e `gameplay.bin` são contêineres VPAK com o par
VLT+BIN embutido. `scripts/vlt_dump.py` lê classes e coleções (hash Jenkins lookup2,
init 0xABCDEF00, conferido: `pvehicle` = 0x4A97EC8F). Resumo em `docs/vlt-slots.json`.

- Não existem nós `_top`. `camaro`, `camaron` e `mustanggt` têm coleções próprias
  em pvehicle, engine, transmission, chassis, tires, brakes, ecar e outras.
  `mustanggt` não tem `induction` nem `nos` próprios.
- **`pvehicle/camaron` herda de `pvehicle/camaro`.** O que o CAMARON não
  sobrescreve muda junto. `transmission/camaron` é coleção própria, então
  `TORQUE_SPLIT` no `camaro` não afeta o Camaro Concept.
- FE: `mustanggt` ← `ford` (ok); `camaro` ← `chevrolet` → trocar para `ford`.
  `camaro_concept` é o nome FE do CAMARON.
- Carro inicial: o modo carreira oferece Camaro SS (muscle), RX-8 e Brera
  ([SuperCheats](https://www.supercheats.com/playstation2/questions/needforspeedcarbon/72951/what-is-the-best-car-to-start.htm)).
  `CAMARO` é o Camaro SS 67. Confirmação definitiva só em jogo.
- O leitor ainda não decodifica valores de campo; para valores e edição, usar VltEd.

## 4. Origem dos doadores e estado do jogo

- `CARS/CAMARO`, `CARS/MUSTANGGT` e `GLOBAL/*` com mtimes de build 2006-10-14/16,
  iguais aos carros intocados; SHA-256 iguais às cópias em `reference/`.
  Evidência forte de que são originais, mas não é prova criptográfica.
- O jogo já tem NFSCUnlimiter, ExtraOptions, WidescreenFix e DLC Unlocker.
- Existem `CARS/911TURBO_backup_stock`, `997TT_backup_stock` e `R32_backup_stock`
  criados em 07/10 entre 01:01 e 01:07 (horário local), e `scripts/*.ini` alterados
  às 01:03. Não fazem parte deste projeto e não foram tocados.

## 5. Ferramentas

- VltEd 4.6 extraído em `tools/vendor/cartoolkit/vlted/` com 7-Zip 24.09 (o arquivo
  usa BCJ2). `NFS-VltEd.exe` SHA-256
  `fe664654f0b1248c978b4e8d6e4cc6a139ba16e3876421c0a12f507e23a743a5`.
  `UserHashes.txt` vazio.

## Próximo passo (exige GUI)

1. nfscgc: XNAME `MUSTANGGT`, entrada `work/carbon2018-source-axes`
   (o `mpoints.txt` dessa pasta precisa estar ao lado dos OBJ; conferir se o
   compilador o lê da pasta de entrada ou da pasta do executável e copiar se preciso).
   No log, conferir “Mount point processed” e nenhum “Not found any part”.
2. CarToolkit → Carbon/Racer/MUSTANGGT → `work/carbon2018-stage-axes`.
3. Reauditar: extrair sólidos, `validate-carbon-solids.ps1`, depois
   `python scripts/dump_position_markers.py <sólidos> <audit> docs/carbon2018-stage-markers.json`.
   Critérios: caixas no sistema do doador (X frente), marcadores com posição igual
   ao relatório e matrizes compatíveis com as do doador.
