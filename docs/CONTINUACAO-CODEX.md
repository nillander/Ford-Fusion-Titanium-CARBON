# Passagem para o Codex — integração AWD do 2018 (07/10/2026)

## Prioridade atual — candidata leve EXOTIC após v1.2 (18:20)

Usuário ainda considera o Fusion pesado e quer uma alternativa customizada à
BMW M3 GTR. Em seguida perguntou se Muscle/Exotic fazem diferença.

Instalado **attributes.bin B5DA3F6865C760D6279B29526D2B8CF83FA3CBAC3694DD88280FFB74CB2580E4**.
Comparação: massa 1600→1100; FINAL_GEAR base 3,06→4,11/top 3,5→4,11;
FLYWHEEL_MASS base 12→10/top 9→10. São cinco campos numéricos e RacingClass;
todo o restante da v1.2
mantido (motor BMW +20%, AWD, direção, pneus/freios/chassi, preço 50.000 e visual).
10.180 nós/312 blobs e rollback auditados; importação sobre v1.2 equivalente.
Gerar com `prepare-performance-2018.py --racer-weight --racing-class Exotic`. Sem as flags reproduz
o acerto de peso anterior; não regenerar sem perceber o modo de comparação.

Rollback ao publicado: `test-install-performance-2018.ps1 -Action RestoreRelease`,
com jogo/VltEd fechados. Fonte work/global2018-performance-v1.2/main/attributes.bin
SHA D58BEA8A…, gate docs/carbon2018-performance-v1.2-verification.json. Restore
sem sufixo continua voltando aos atributos do Mustang original.

**Usuário escolheu EXOTIC; instalado:** override local RacingClass sem trocar
o pai. Herança original mustanggt → muscle → racers;
BMW → exotic → racers. RacingClass herdado, ausente no Data próprio do Mustang.
Racer não equivale à classe Exotic. Pais muscle/exotic têm MASS=1000 e mesmo
TENSOR_SCALE=(1,2,1,0); peso extra era override. Classe aparece em regras,
música/recompensas e SkidInfo; efeito direto sobre física não foi estabelecido.
Diagnóstico em docs/carbon2018-racing-class-diagnostic.json. Override Exotic
auditado no próprio slot, sem reparentear o Mustang. Rollback remove o override
(delete_field) e restaura a herança exata; comprovado na auditoria de todos os nós.
Documentação oficial ModScript confirma add_field/delete_field/update_field.
Não alterar flags booleanas desconhecidas nem Tier 2 sem motivo comprovado.

Usuário respondeu Exotic e disse que testará quando terminar. Aguardar QA da
categoria no menu e arrancada/retomada/curvas. Backup só leve, ainda Muscle,
em work/global2018-performance-lightweight (4277ECF9…), gate próprio preservado.
Nova candidata
não publicada; v1.2 permanece intacta e o empacotador impede rebatizá-la como v1.2.

## Histórico — v1.2 e motor BMW +20%

Usuário confirmou "tudo certo": direção, logotipo e fogo aprovados. Autorizou
explicitamente **commit, push, tag e release** nesta rodada, substituindo a
restrição antiga de publicação dos históricos abaixo. **v1.2 publicada**, tag
anotada em `ed9b9fe`; branch main e tag enviados. URL:
https://github.com/nillander/Ford-Fusion-Titanium-CARBON/releases/tag/v1.2
ZIP e dois arquivos SHA256SUMS publicados; todos os digests remotos iguais
aos locais. Registro em docs/release-v1.2-verification.json.

Pedido posterior: motor do Fusion 20% acima da BMW M3 GTR jogável. Referência
correta pvehicle bmwm3gtre46 → engine bmwm3gtre46, não o engine bmwm3gtr solto.
TORQUE da BMW ×1,20 e MAX_RPM 9500/RED_LINE 8500/IDLE 800 iguais à referência,
nos nós engine/mustanggt e mustanggt_top. Base/top têm o mesmo alvo de curva;
indução/nitro do slot continuam independentes. Não prometer aceleração 20% maior.
Somente esses seis campos de motor mudaram em relação ao acerto aprovado.

GLOBAL/attributes.bin atual **D58BEA8A066735CC07A36D2D77107254C85523B89369541C481C166A66FF853D**.
Instalado com NFSC/VltEd fechados; auditados 10.180 nós/312 blobs, importação
sobre versão anterior e rollback exato. Direção/AWD/preço 50.000 mantidos.
Backup do acerto aprovado anterior em work/global2018-performance-approved;
gate docs/carbon2018-performance-approved-verification.json. O motor novo
ainda precisa de QA em corrida; publicação autorizada pelo usuário mesmo assim.

Geometria/logo/idiomas são os aprovados abaixo. Release local/release-v1.2:
ZIP, SHA256SUMS e hashes de conteúdo. Instalador portátil verifica 22 destinos,
recusa hashes desconhecidos e preserva estado anterior em Fusion2018_v1.2_backup;
desinstalar restaura também GLOBAL/frontend/idiomas. Manifesto compilado em
release/pacote/arquivos-v1.2.json. Não sobrescrever outros mods manualmente.
scripts/test-release-package.py verificou ZIP, instalar/reinstalar/restaurar e
preflight sem alterações diante de destino desconhecido/pacote corrompido.

Próximos: QA do novo motor; Fusion 2012 FWD usando **CAMARO oficial**, preservar
CAMARON. ON de freio/faixas de fábrica e QA ampliado damage/IA continuam pendentes.
Consultar README/download v1.2 para publicação; não confundir histórico com estado atual.

## Histórico — terceira candidata instalada (07/10, 17:18), posteriormente aprovada

Usuário confirmou o **nome Fusion**, mas a segunda candidata continuou difícil
de virar. Também relatou fogo abaixo das ponteiras e logotipo Mustang GT no menu.
Esses relatos reabrem apenas esses ajustes do 2018; lentes/teto continuam aprovados.

**Instalado, ainda sem confirmação no jogo:**

- attributes.bin `547C601A5517A487AA02ED6F45D0AB9B2CA7FC3CB085D090A3AC270F858B7C06`.
  AWD 0,5, preço 50.000; diferencial 0,35/0,5/0,5; grip dianteiro/traseiro
  igual ao valor dianteiro MW; YAW_CONTROL do Mustang oficial, YAW_SPEED 0,3.
  STEERING 1,1 e ângulo +15% mantidos. É comparação, sem causa comprovada.
- GEOMETRY `4C8CFDF9CEAC10DB58278A2CCA0243C43F4E0A560239AFCA821D36A898E9F65C`.
  60 EXHAUST em 30 BODY (6 kits × 5 LODs), só Z 0,135→0,177339 m, medido nas
  ponteiras cromadas. 160 outros sólidos intactos; 190 passaram no leitor.
  EXHAUST Carbon usa hash explícito `66A4A9DE` de `mp.txt`, não bin_hash('EXHAUST').
- FRONTB1.BUN `D36FA8AC87945B898C5AEB4425EA2A723CE26620B15BA47CCBB50087373D82AB`;
  FrontB1.lzc `5EAC022D3EF04A4FFDAC1B3BA4D02FE0C3FA0081C5113BD4E94BE257E840FF2D`.
  SECONDARY_LOGO_MUSTANGGT (710ABB50), pixels Fusion da referência MW convertidos
  DXT3→ARGB8888/BGRA do doador oficial Carbon; hash/header 256×64/1 mip intactos.
  Só 65.536 bytes de pixels mudam no BUN; resto byte-idêntico. LZC espelha BUN.
  Leitor independente passou nas 264 texturas da primeira TPK.

TEXTURES/VINYLS, idiomas/nome aprovado, FE_ATTRIB e CAMARO/CAMARON não mudaram
nesta correção. Não atualizar a release v1.1 sem aprovação do novo QA.

**Próxima ação:** receber teste de curvas em baixa velocidade/corrida/base/upgrades,
fogo e logotipo no menu. Se direção continuar ruim, investigar com uma comparação
controlada; não aumentar novamente o ângulo às cegas nem declarar o diferencial
como causa certa. Só avançar ao 2012 depois dessa validação.

Reprodução: `prepare-performance-2018.py` + CLI Attribulator + auditoria VLT;
`prepare-exhaust-2018.py`; `prepare-frontend-logo-2018.py`;
`verify-corrections-2018.py` executa leitores e aprova gates.
Instalar/restaurar conjunto: `test-install-corrections-2018.ps1 -Action Install/Restore`,
com NFSC/VltEd fechados. Restore volta **ao segundo teste**, geometria v1.1 e
logo original; mantém nome Fusion. Backup transacional listado em
`docs/carbon2018-corrections-install.json`. Originais Frontend em
`work/frontend-before-logo-2018`, segundo VLT em `work/global2018-performance-second`.
As duas primeiras candidatas e seus gates ficam preservados.

Ao parar: atualizar documentos e commit com `Co-authored-by: Codex <codex@openai.com>`.
Não push/tag/release. Doador 2018 MUSTANGGT oficial; 2012 CAMARO oficial, preservar CAMARON.

## Histórico da integração anterior — substituído pela prioridade acima

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
