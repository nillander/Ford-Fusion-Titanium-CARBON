# v1.1 — Fusion 2018 no Need for Speed Carbon

Atualização do Ford Fusion Titanium 2018 para o Need for Speed Carbon (slot
`MUSTANGGT`). Inclui a entrada de ar do teto e a correção do compressor JDLZ
exigida pelo jogo. Nome, logotipo e performance ainda são os do Mustang GT; o
Fusion 2012 ainda não foi portado.

- **Entrada de ar do teto:** `KIT00_ROOF_A..D` e `ROOF_SCOOP` recompilados (190
  malhas). Aparecem nas opções comum e AutoSculpt.
- **Compressor JDLZ:** preserva as flags terminais que o Carbon exige ao
  descomprimir; streams antigos são normalizados antes da instalação.
- Mantém da v1.0: carroceria no padrão Carbon, faróis/lanternas/refletores e
  aerofólios da loja alinhados à tampa do porta-malas.

**Limitações conhecidas:** nome, logotipo, preço, performance e tração (traseira)
continuam os do Mustang GT. A lanterna não acende mais forte ao frear. Adesivos
de fábrica do Mustang podem aparecer fora do lugar. Corrida completa, dano e
rivais ainda não foram testados.

## Instalar

Feche o jogo, extraia `Fusion2018_AWD_NFSC.zip` e execute `instalar.bat`. O script
procura o jogo, guarda o Mustang GT original em `CARS\MUSTANGGT_original` e copia o
Fusion para `CARS\MUSTANGGT`. Para voltar ao original, execute `desinstalar.bat`.
Confira os arquivos com `SHA256SUMS.txt`.
