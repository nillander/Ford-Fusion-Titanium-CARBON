# Ford Fusion Titanium 2018 AWD — Need for Speed Carbon

Substitui o **Ford Mustang GT** (slot `MUSTANGGT`). Release v1.1 de 07/10/2026.

Port da carroceria do Fusion 2018 da release MW2005 v2.8 para o Carbon. O visual
está pronto (incluindo a entrada de ar do teto), mas o carro ainda usa o nome,
o logotipo e a performance do Mustang GT.

## O que vem no pacote
- **Visual**: carroceria do Fusion Titanium 2018 com rodas, vidros, emblemas e os
  cinco níveis de detalhe, convertida para o Carbon (190 peças, orientação e pontos
  de montagem do Carbon), com entrada de ar do teto (comum e AutoSculpt).
- **Luzes**: faróis, farol de milha, lanternas e refletores traseiros usando as
  luzes dinâmicas do Carbon, com os materiais do Mustang GT original.
- **Aerofólios da loja**: pontos de montagem ajustados à tampa do porta-malas do
  Fusion, inclusive os do AutoSculpt.

## Limitações conhecidas
- Nome, logotipo e preço continuam os do **Mustang GT**.
- Performance e tração são as do **Mustang GT** (traseira). Ainda não há AWD.
- A lanterna não acende mais forte ao frear.
- Adesivos de fábrica do Mustang podem aparecer fora do lugar.
- Ainda não testados: corrida completa, dano, rivais e IA que usam o Mustang GT.
- O Fusion 2012 FWD (slot Camaro) ainda não foi portado.

## Requisitos
- Need for Speed Carbon (PC). Não precisa de Unlimiter nem de outro mod.

## Instalação
1. Extraia o ZIP. Ele abre numa pasta com o mesmo nome do arquivo.
2. Feche o jogo e execute `instalar.bat` nessa pasta. O script procura o jogo,
   guarda o Mustang GT original em `CARS\MUSTANGGT_original` (só na primeira vez)
   e copia `GEOMETRY.BIN` e `TEXTURES.BIN` para `CARS\MUSTANGGT`.
3. Abra o jogo. O Fusion 2018 aparece no lugar do Mustang GT.

Para desinstalar, feche o jogo e execute `desinstalar.bat`. Ele copia de volta
`CARS\MUSTANGGT_original`. Confira os arquivos com `SHA256SUMS.txt`
(ex.: `certutil -hashfile GEOMETRY.BIN SHA256` no Windows).

## Créditos
Modelo GTA V: AND1V79; conversão e texturas para o GTA V pelo autor do pacote
original, disponibilizado por Gabriel Lima (ver `CREDITOS/source-readme.txt`).
Base MW (Fusion 2010): Marcelo Castro (AJM3899), com peças de FOX, Porsche4ever e
AJ Lethal (ver `CREDITOS/donor-readme.txt`).
Ferramentas Carbon: NFS-CarToolkit 3.1 e NFS Carbon ModTools 1.1 (nfsu360),
compressor JDLZ de OpenNFSTools (zombie28), meshoptimizer.
Estrutura, materiais e pontos de montagem de referência: Ford Mustang GT original
do Need for Speed Carbon.
Conversão para o Carbon: Nillander Alarcão, com Codex e Claude.
