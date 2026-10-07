# Fusion 2018 — candidata de performance Carbon

Acerto MW v2.8 convertido para o Carbon, com AWD por escolha do usuário.
Preço original do Mustang (50.000), desbloqueio, fabricante Ford e montagem
visual preservados. Este script não muda nome/logotipo e não faz parte da v1.1.

Primeiro teste: o carro carregou, condução geral boa, dificuldade para virar
mesmo em baixa velocidade. A candidata atual restaura a escala de direção
original do Carbon e amplia em 15% sua curva de ângulo, na base e nos upgrades.
Essa comparação ainda aguarda aprovação no jogo.

Com jogo fechado, faça backup de GLOBAL. Abra a pasta do Carbon no NFS-VltEd 4.6,
importe `Fusion2018-performance.nfsms` em File → Import → ModScript, confira
ausência de erros e salve. Attribulator 2.0 também aplica esse script por CLI.

Para recuperar somente os campos afetados, importe
`Fusion2018-performance-rollback.nfsms`. O rollback usa os valores da instalação
original deste projeto. Não usá-lo para restaurar modificações de outros mods
que tenham sido aplicadas depois. Não renomear/excluir nós nem reutilizar
offsets do MW. CAMARO e CAMARON não são alterados.

Para reproduzir a candidata, consulte README e
`docs/carbon2018-performance-verification.json`. Motor, suspensão, pneus e freios
são adaptação do acerto de jogo do MW; não são especificações de fábrica do Fusion.
