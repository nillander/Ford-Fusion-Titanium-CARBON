# v1.2 — Fusion Titanium AWD 2018 no Carbon

O Fusion agora tem nome e logotipo próprios, tração AWD e direção aprovada no
jogo. O fogo do escapamento foi alinhado às ponteiras. O preço original de
compra do slot Mustang GT permanece **50.000**.

- Mantém carroceria, lentes, rodas, aerofólios e entradas de ar da v1.1.
- Nome Ford Fusion Titanium AWD nos 17 arquivos de idiomas; logotipo Fusion
  no recurso SECONDARY_LOGO_MUSTANGGT do frontend.
- AWD 50/50, direção corrigida na base e nos upgrades.
- 60 pontos de fogo reposicionados em todos os seis kits e cinco LODs.
- **Motor: curva de torque da BMW M3 GTR jogável (bmwm3gtre46) × 1,20**, com
  MAX_RPM 9500 e RED_LINE 8500 iguais à referência, na base e no motor melhorado.
  Define a curva de potência do motor 20% acima da referência no mesmo domínio
  de RPM. Nitro, indução, massa e relações de marcha afetam o resultado na pista;
  não significa velocidade final ou aceleração 20% maiores.

Direção, nome, logotipo e escapamento foram confirmados pelo usuário no jogo.
O ajuste posterior de potência foi solicitado e autorizado para esta release;
passou na auditoria completa, mas ainda não teve novo teste em corrida.
10.180 nós/312 blobs verificados, somente 11 nós do Fusion alterados;
BMW, CAMARO/CAMARON e demais carros preservados. Rollback validado.

## Instalação e restauração

Extraia `Fusion2018_AWD_NFSC.zip`, feche NFSC/NFS-VltEd e execute `instalar.bat`.
O instalador identifica a pasta do jogo e verifica os hashes de todos os 22
arquivos antes de copiar. Inclui GEOMETRY/TEXTURES, GLOBAL/attributes.bin,
FRONTB1.BUN/LZC e os idiomas Frontend. Guarda o estado anterior em
`Fusion2018_v1.2_backup`. `desinstalar.bat` restaura esse estado, inclusive se
a instalação anterior era a v1.1. Backups são mantidos.

O pacote binário é destinado à base Carbon verificada neste projeto. Arquivos
com hashes de outra versão/mod são recusados antes da instalação. Para combinar
performance com outros mods, use o `.nfsms` em `VLT/` com VltEd/Attribulator;
nome/logotipo precisam ser integrados separadamente nesse caso. Não copiar
attributes.bin ou FRONTB1 manualmente sobre outra configuração modificada.
Confira o ZIP e seu conteúdo com os arquivos SHA256SUMS.

Pendentes: iluminação de freio ON distinta de OFF, faixas Mustang de fábrica,
QA ampliado de damage/IA e o port do Fusion 2012 FWD no CAMARO oficial.
