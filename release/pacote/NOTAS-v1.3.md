# v1.3 — Fusion Titanium AWD 2018 EXOTIC no Carbon

O Fusion no slot MUSTANGGT passa a usar massa 1100, relação final 4,11 e
volante do motor 10, iguais à referência BMW M3 GTR jogável. A categoria
EXOTIC é um override local: o pai original do Mustang e o Tier 2 permanecem.

- Mantém AWD 50/50, direção corrigida, preço de compra original **50.000**,
  carroceria, lentes, rodas, aerofólios, teto, nome e logotipo Fusion.
- Mantém a curva de torque BMW `bmwm3gtre46` ×1,20, com o mesmo domínio de RPM,
  na base e no motor melhorado. Isso não promete aceleração ou velocidade
  final 20% maiores.
- Corrige a comparação de peso: a massa anterior 1600 deixava a relação
  potência/peso 17,5% abaixo da BMW, apesar do motor +20%.
- Somente seis campos mudam frente à v1.2: massa, duas relações finais,
  dois volantes do motor e RacingClass. Outros carros permanecem intactos.

Visual, direção anterior, nome, logotipo e fogo foram confirmados no jogo.
O motor posterior e o novo acerto leve EXOTIC passaram nas auditorias, mas
**a confirmação em corrida e da categoria no menu ainda está pendente**.
A publicação foi solicitada pelo usuário com esse estado registrado.
Auditoria completa: 10.180 nós, 312 blobs, 11 nós do Fusion e 74 campos
alterados frente à base; rollback semanticamente idêntico e importação sobre
v1.2 equivalente. Não foi demonstrado um efeito direto da classe na física.

## Instalação e restauração

Extraia o ZIP, feche NFSC/NFS-VltEd e execute `instalar.bat`.
Os 22 arquivos são conferidos antes de qualquer cópia: geometria/texturas,
GLOBAL/attributes.bin, FRONTB1.BUN/LZC e 17 idiomas Frontend.
O estado anterior fica em `Fusion2018_v1.3_backup`. `desinstalar.bat` restaura
esse estado, inclusive quando era a v1.2, preservando os backups anteriores.

O pacote aceita somente os hashes das bases e candidatas verificadas neste
projeto. Outra versão/mod é recusada antes da cópia. Para combinar performance
com outros mods, use os ModScripts de `VLT/`; integre nome/logotipo à parte.
Confira o ZIP e o conteúdo pelos arquivos SHA256SUMS.

Pendentes: QA do acerto leve EXOTIC, freio ON distinto de OFF, faixas Mustang
de fábrica, damage/IA e Fusion 2012 FWD no CAMARO. A alternativa Fusion AWD
no **SL65 AMG oficial** foi adicionada ao TODO; ainda não está construída nem
incluída nesta release. Seu possível benefício requer comparação no jogo.
