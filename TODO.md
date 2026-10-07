# TODO — Portar Ford Fusion (MW2005) → Need for Speed Carbon

Portar os dois Fusion do `../fusion-mw2005` (v2.8) para o Carbon: **2012 FWD** e **2018 AWD**, por **substituição de slot** (não add-on).

## Premissas (assumidas)

| Item | Caminho |
| --- | --- |
| Jogo Carbon | `D:\Program Files (x86)\Electronic Arts\Need for Speed Carbon` |
| Fonte MW (Fusion 2012/2018) | `C:\Users\nillander\NoDocuments\fusion-mw2005` |
| Release MW de partida | `fusion-mw2005/release/` → `Fusion2012_FWD_MW2005.zip`, `Fusion2018_AWD_MW2005.zip` (v2.8) |

### Mapeamento de slots

| Carro | Slot MW | Slot Carbon | Papel no Carbon |
| --- | --- | --- | --- |
| Fusion Titanium 2012 FWD | `COBALTSS` | **`CAMARO`** | Chevrolet Camaro do **início** da carreira |
| Fusion Titanium 2018 AWD | `MUSTANGGT` | **`MUSTANGGT`** | Mustang GT (mesmo XNAME do MW) |

> No Carbon existem `CAMARO` e `CAMARON`. O alvo do 2012 é **`CAMARO`** (carro inicial). Não tocar em `CAMARON` salvo necessidade futura.

### Regra obrigatória dos doadores (instrução do usuário)

Usar como doadores **os veículos oficiais do Carbon que serão substituídos**:
**CAMARO oficial → Fusion 2012 FWD** e **MUSTANGGT oficial → Fusion 2018**.
Preservar deles a estrutura e os recursos exigidos pelo slot (peças, LODs, kits,
AutoSculpt, damage, materiais e pontos de montagem), adaptando a malha Fusion MW.
Não usar outro veículo/mod como base Carbon. Confirmar a origem limpa dos BIN
antes de considerar o doador validado; a cópia da instalação atual não comprova isso.

Tração alvo (herdada do MW):

| Carro | Tração |
| --- | --- |
| 2012 no `CAMARO` | FWD (`TORQUE_SPLIT` 1,0) |
| 2018 no `MUSTANGGT` | RWD no VLT (`TORQUE_SPLIT` 0); nome de garagem AWD |

---

## Como a comunidade faz o port (resumo da internet)

Fontes principais (úteis mesmo em replace):

- [Binary (NFSCO)](https://github.com/NFSCO/Binary) / [nfsmods Binary](https://nfsmods.xyz/mod/1638) — edita `.BIN`/`.BUN`/`.LZC` via `.end` (não edita VLT nem geometry “crua”)
- [NFS-VltEd](https://nfs-tools.blogspot.com/2017/01/nfs-vlted-usage-update-24012017.html) — importa `.nfsms` (performance, FE, pvehicle…)
- [nfsu360 Carbon ModTools](https://nfs-tools.blogspot.com/2010/05/nfscarbon-modtools-v10-released.html) — geometry compiler Carbon
- [NFS Modder's Corner — MW → add-on](https://nfsmodderscorner.blogspot.com/2018/12/how-to-convert-nfsmw-modloader-car-to.html) — conversão ModLoader→dados; adaptar para **retarget de XNAME** (`COBALTSS`→`CAMARO`, `MUSTANGGT`→`MUSTANGGT`)
- Performance MW→Carbon via VltEd: [MW Parts](https://nfsmods.xyz/mod/520)

### Fluxo deste projeto (replace de slot)

1. Backup de `CARS/CAMARO`, `CARS/MUSTANGGT` e de `GLOBAL` / VLT afetados.
2. Recompilar geometry/textures MW com **Game = Carbon** e XNAME do slot alvo (`CAMARO` / `MUSTANGGT`).
3. Copiar `GEOMETRY.BIN` + `TEXTURES.BIN` (e vinis se houver) para `CARS/<slot>/`.
4. **NFS-VltEd**: `.nfsms` que altera FE (nome Ford Fusion…) e performance nos nós `camaro` / `mustanggt` (e variantes `_top` se existirem).
5. **Binary** só se precisar de strings/logo/global — não é obrigatório Unlimiter para replace puro.
6. Testar com save novo ou save no início (Camaro).

> O pacote MW usa **Mod Loader** (`ADDONS` + `.MWPS`). No Carbon isso **não** existe: performance/FE vão para **VLT** (`.nfsms`). Geometry precisa **reexport Carbon** com o XNAME do slot.

### O que NÃO é drop-in

| MW | Carbon |
| --- | --- |
| `ADDONS/CARS_REPLACE/<slot>/*.MWPS` | Nós VLT via `.nfsms` nos slots `CAMARO` / `MUSTANGGT` |
| `CAR.INI` + Mod Loader | Replace direto em `CARS/<slot>` + VltEd |
| Slot `COBALTSS` | **`CAMARO`** (retarget de sólidos/hashes) |
| Slot `MUSTANGGT` | **`MUSTANGGT`** (mesmo nome; ainda assim recompilar para Carbon) |
| Geometry `mwgc` (MW) | CarToolkit/ModTools **alvo Carbon** |

---

## Ferramentas necessárias

- [ ] **Binary** ≥ 2.9 (strings/logo/global se necessário)
- [ ] **NFS-VltEd** ≥ 4.6 (FE + performance nos slots)
  - [x] Extraído em `tools/vendor/cartoolkit/vlted/` (7-Zip; SHA-256 em `docs/SESSAO-CLAUDE-2026-10-07.md`); ainda não operado
  - [x] Leitor próprio somente-leitura do VPAK Carbon: `scripts/vlt_dump.py` (classes/coleções/pais; não lê valores de campo)
- [x] **NFS-CarToolkit 3.1** e **Carbon ModTools 1.1**, obtidos e operados; proveniência em `tools/README.md`
- [ ] Backup limpo do Carbon (já há pasta `Backup` no jogo)
  - [x] Doadores e GLOBAL conferidos byte a byte com `reference/` (SHA-256 iguais em 07/10 02:40)
- [x] Espelhar utilitários MW selecionados e RetargetSlot em `tools/vendor/mw`; manifesto em `tools/toolchain-manifest.json` (não convertem formato para Carbon)
- [ ] Unlimiter **não** é requisito para este replace; só se o jogo já estiver modado com add-ons
  - Nota 07/10: o jogo **já tem** NFSCUnlimiter, ExtraOptions, WidescreenFix e DLC Unlocker em `scripts/`; considerar no QA

---

## Fase 0 — Setup do repositório

- [x] Espelhar estrutura mínima do MW: `source/`, `tools/`, `scripts/`, `versions/`, `release/`, `docs/`, `capturas/`, `work/`
- [x] Documentar em `README.md` os caminhos do jogo e a origem `../fusion-mw2005`
- [x] Extrair v2.8 MW para `reference/mw-v28/` (SHA-256 dos ZIPs conferidos):
  - [x] `MUSTANGGT` → Fusion 2018 (destino Carbon: `MUSTANGGT`)
  - [x] `COBALTSS` → Fusion 2012 (destino Carbon: `CAMARO`)
- [x] Copiar referência instalada Carbon: `CARS/CAMARO` e `CARS/MUSTANGGT` → `reference/carbon-stock/`; backup GLOBAL em `reference/carbon-global-before/`
- [x] Confirmar origem oficial/vanilla dos doadores copiados — evidência forte, não criptográfica: BIN de `CAMARO`/`MUSTANGGT` e `GLOBAL/*attrib*` com mtime de build 2006-10-14/16, iguais aos carros intocados; sem `_backup_stock` desses slots (ver sessão 07/10)
- [ ] Inventariar peças/sólidos do MW e do stock Carbon (kits, AutoSculpt, spoiler AS, damage) e mapear o que falta no port
  - [x] Descomprimir e nomear 848 CAMARO + 997 MUSTANGGT; leitura independente das 1845 malhas
  - [x] Mapa inicial MUSTANGGT: 86 correspondências exatas com os 186 sólidos Fusion MW; 911 nomes do doador sem correspondência exata (não significa 911 peças obrigatórias)
  - [ ] Adaptar o mapa aos recursos efetivamente exigidos pelo slot oficial

---

## Fase 1 — Slots (fechado)

Decisão:

| Fusion | Substitui | Pasta |
| --- | --- | --- |
| 2012 FWD | Chevrolet Camaro (início) | `CARS/CAMARO` |
| 2018 AWD | Mustang GT | `CARS/MUSTANGGT` |

- [x] Slots Carbon definidos: `CAMARO` + `MUSTANGGT`
- [x] Confirmar no VLT/FE que `CAMARO` é o carro inicial da carreira (não `CAMARON`): `CAMARO` = Camaro SS 67 (opção muscle inicial, ao lado de RX-8 e Brera); `CAMARON` = `camaro_concept` no FE. Prova final só em jogo
- [x] Listar nós VLT a editar: não existem `_top`; coleções `camaro`/`mustanggt` em pvehicle, engine, transmission, chassis, tires, brakes, induction, ecar e mais 6 classes (`docs/vlt-slots.json`)
  - **Atenção:** `pvehicle/camaron` herda de `pvehicle/camaro`. Campos que `camaron` não sobrescreve mudam junto; `transmission/camaron` é coleção própria (FWD no `camaro` não afeta o CAMARON)
- [x] Confirmar manufacturer Ford no FE de ambos: `frontend/mustanggt` herda de `ford` (ok); `frontend/camaro` herda de `chevrolet` → precisa mudar para `ford` no VltEd
- [ ] Decidir se 2018 fica RWD (como MW VLT) ou tenta AWD real no Carbon
- [ ] 2012: forçar FWD no VLT do Camaro (stock Camaro é RWD — precisa mudar `TORQUE_SPLIT` e sensação)

---

## Fase 2 — Geometria e texturas

- [ ] Abrir `GEOMETRY.BIN` MW no CarToolkit; reexportar com **Game = Carbon**
  - [x] 2018: exportação preliminar Carbon em `work/carbon2018-stage`, 186 sólidos MUSTANGGT validados; compatibilidade com doador ainda pendente
  - [ ] 2012: retarget `COBALTSS` → `CAMARO` (renomear sólidos/marcadores)
- [ ] Reexportar `TEXTURES.BIN` no mesmo XNAME; nomes ≤ 23 chars
- [ ] Validar ≤ 65535 vértices **e índices**/sólido; LODs; kits que cutscenes/IA do slot pedem
  - [x] Resolver `Indices count for MUSTANGGT_BASE_A exceeded 65536`: simplificar 13 malhas apenas em staging, máximo 65397 índices; conferir 186 malhas reexportadas
  - [x] Reexportar e ler independentemente 10 texturas Carbon; nomes de luzes encurtados para ≤ 23 caracteres
  - [ ] QA visual da simplificação, materiais, cores de vértices, bordas e UVs
- [ ] DXT1 em opacos; DXT3 só lente/vidro
- [ ] **BLOQUEADOR (07/10): staging 2018 está girado 90° no eixo Z.** O nfscgc grava (x′,y′)=(y,−x); doador tem X frente, staging tem Y frente. Fonte corrigida em `work/carbon2018-source-axes` (`scripts/prepare-compiler-input.py`); recompilar no GUI e reauditar
- [ ] Mount points vs stock `CAMARO` / `MUSTANGGT` (rodas, exhaust, spoiler, luzes)
  - [x] Extrair marcadores do doador (`docs/mustanggt-stock-markers.json`, 296; `docs/camaro-stock-markers.json`, 276) e do MW (`docs/mw2018-markers.json`, `docs/mw2012-markers.json`)
  - [x] `mpoints.txt` + 165 OBJ de ponto de montagem para o 2018 (lados normalizados LEFT=+Y; anexos iguais ao doador)
  - [ ] Compilar, conferir posições e matrizes dos marcadores contra o doador
  - [ ] Sem fonte ainda: `LICENSEPLATE`, `ROOF_SCOOP` (Fusion não tem `KIT00_ROOF`), `LEFT/RIGHT_EXHAUST` dos para-choques
- [ ] Smoke-test: início da carreira com Fusion 2012; Mustang slot com Fusion 2018

---

## Fase 3 — Dados Binary (`.end`) — opcional / mínimo

- [ ] Só se precisar: language strings (“Ford Fusion…”), logo fabricante, ajustes Global
- [ ] Não criar CarTypeInfo de add-on — os slots já existem
- [ ] Manter `Install.end` pequeno ou pular se só BIN + VLT bastarem
- [ ] Backup antes de qualquer apply

---

## Fase 4 — Dados VltEd (`.nfsms`)

- [ ] Converter `ATTRIBUTES.MWPS` MW → nós Carbon:
  - [ ] `mustanggt`: intent SLR motor + chassi Mustang (v2.1 MW)
  - [ ] `camaro`: chassi/base do 2018 + motor FWD (estilo Cobalt ×1,2) com `TORQUE_SPLIT` 1,0
- [ ] Converter `FE.MWPS` → nomes de garagem:
  - [ ] Camaro → `Ford Fusion 2012 FWD` (manter preço/disponibilidade de carro inicial se possível)
  - [ ] MustangGT → `Ford Fusion Titanium AWD` (preço/tier alinhados ao MW ou ao Mustang Carbon)
- [ ] Importar `.nfsms`, Save, testar save no início + Mustang na seleção
- [ ] Comparar sensação com MW

---

## Fase 5 — Frontend / logos / vinis

- [ ] Logo / secondary logo dos slots via Binary ou replace de textures frontend
- [ ] Vinis: UV contínua; adaptar `VINYLS.BIN` de `CAMARO` / `MUSTANGGT` se o port quebrar adesivos
- [ ] Strings de idioma se o nome stock ainda aparecer

---

## Fase 6 — Empacotamento e release

- [ ] Layout de release:

  ```text
  release/
    Fusion2012_FWD_NFSC/
      CARS/CAMARO/GEOMETRY.BIN
      CARS/CAMARO/TEXTURES.BIN
      Install.nfsms          # FE + FWD no nó camaro
      instalar.bat / LEIA-ME.md
    Fusion2018_AWD_NFSC/
      CARS/MUSTANGGT/GEOMETRY.BIN
      CARS/MUSTANGGT/TEXTURES.BIN
      Install.nfsms
      instalar.bat / LEIA-ME.md
  ```

- [ ] Instalador: backup automático de `CARS/CAMARO` e `CARS/MUSTANGGT` antes de copiar
- [ ] SHA-256 dos BIN
- [ ] Capturas (`capturas/2012`, `capturas/2018`)
- [ ] Notas + créditos

---

## Fase 7 — QA no Carbon

- [ ] **Início da carreira**: spawn / escolha com Fusion 2012 no lugar do Camaro
- [ ] Seleção: Mustang GT mostra Fusion 2018 (nome + logo)
- [ ] Garagem: kits, hoods, spoiler, wheels, paint, vinyl em ambos os slots
- [ ] Luzes dia/noite
- [ ] Perseguição / damage / LODs
- [ ] Dirigibilidade FWD no Camaro-slot vs RWD/AWD no Mustang-slot
- [ ] IA / rivais que usam `CAMARO` ou `MUSTANGGT` não ficam sem carroceria
- [ ] Comparar visual com v2.8 MW

---

## Ordem sugerida de trabalho

1. Setup repo + extrair MW v2.8 + dump stock `CAMARO` / `MUSTANGGT`  
2. Recompilar **2018 → MUSTANGGT** (mesmo XNAME, base compartilhada)  
3. VltEd mínimo no Mustang → carro andando  
4. Retarget **2012 → CAMARO** (geometry + FWD no VLT)  
5. Confirmar início da carreira  
6. Logos/vinis → release  

---

## Riscos conhecidos

- Kit/body ausente = carro invisível (IA, cutscenes, presets do slot)
- Camaro stock é RWD — esquecer `TORQUE_SPLIT` FWD deixa o 2012 errado
- Substituir `CAMARO` afeta qualquer conteúdo que use esse slot (rivais, eventos)
- DXT3 em opaco / textura > 23 chars / UV 0–1 nas luzes (aprendizados MW)
- Geometry MW sem reexport Carbon = hash/XNAME errado mesmo com pasta certa
- Editar VLT sem backup = save quebrado

---

## Referências rápidas

| Assunto | Link |
| --- | --- |
| Binary | https://github.com/NFSCO/Binary |
| VltEd usage | https://nfs-tools.blogspot.com/2017/01/nfs-vlted-usage-update-24012017.html |
| Carbon ModTools | https://nfs-tools.blogspot.com/2010/05/nfscarbon-modtools-v10-released.html |
| MW ModLoader → dados de carro | https://nfsmodderscorner.blogspot.com/2018/12/how-to-convert-nfsmw-modloader-car-to.html |
| Performance MW→Carbon (VLT) | https://nfsmods.xyz/mod/520 |

Estado do código-fonte MW e aprendizados: `../fusion-mw2005/README.md`, `docs/APRENDIZADOS.md`, `docs/CONTINUACAO.md`.

---

## Passagem para Claude — 07/10/2026, 02:31 (America/Sao_Paulo)

Leia **`docs/CONTINUACAO-CLAUDE.md`** para assumir a partir deste commit.
Codex descomprimiu e validou 1845 malhas dos doadores instalados. Exportou o
Fusion 2018 para Carbon em staging: 186 sólidos e 10 texturas com leitura independente.
O limite de índices foi resolvido simplificando 13 malhas; fontes v2.8 intactas.
Nenhum arquivo do jogo foi alterado; sem instalação ou QA em jogo.

Próximo passo: confirmar origem oficial dos doadores e adaptar o staging ao MUSTANGGT
oficial: pontos de montagem, kits, LODs, AutoSculpt, damage e materiais. A saída ainda
não é um port instalável. O Fusion 2012 permanece na etapa de referências.
O horário acima é a retomada informada pelo usuário, não uma automação criada aqui.
