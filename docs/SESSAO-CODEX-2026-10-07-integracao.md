# Integração do Fusion 2018 — 07/10/2026

O usuário considera o visual 2018 finalizado e pediu avançar no TODO.
Decisões confirmadas: AWD real no Carbon e manter preço original de compra 50.000.
Geometria/texturas aprovadas da v1.1 preservadas. Doador Carbon continua MUSTANGGT
oficial; para o próximo carro usar CAMARO oficial e preservar CAMARON.

VltEd mostrou frontend Cost 50000, manufacturer 2 e UnlockedAt 11. O teste de
preço 42000 ficou só na memória e foi descartado após a instrução do usuário.
Nomes visíveis não estão em um campo de texto desse nó VLT.

Attribulator 2.0 foi obtido da release oficial e executado via CLI para extrair
a base completa em YAML e aplicar scripts em staging. Corrige o inventário
inicial: existem níveis mustanggt_top e indução mustanggt_base/top.
Os offsets MW não são portáveis. A conversão usa nomes e tipos Carbon, com
membros Front/Rear, índices de arrays e contagem real de marchas.

Performance gerada: 76 campos de 11 nós, massa/inércia, motor, transmissão,
chassi, pneus e freios. AWD 0,5 e centro do diferencial 0,75 na base e upgrade.
ecar, altura visual, áudio/indução/nitro e campos específicos de drift preservados.
Auditoria compara 10.180 nós e 312 blobs, exige só alterações planejadas e
rollback semanticamente idêntico. Instala somente GLOBAL/attributes.bin.

Primeiro teste no jogo: carregou; condução geral boa, porém difícil virar mesmo
em baixa velocidade. Primeiro BIN e relatório preservados em
work/global2018-performance-first e carbon2018-performance-first-verification.json.
Comparação instalada: escala de direção original 1,1 e curva de ângulo +15%,
base e upgrades; todo o resto igual ao primeiro teste. Hash attributes atual:
9DECD6C74E3E182468AE625C975213C2C6D311C6978D22086AB2783367899F1C.
Confirmação de direção solicitada ao usuário; ainda pendente.

Nome: CARNAME_FORD_MUSTANGGT foi identificado por Labels_Frontend (hash 1CC69F99).
Preparados/auditados e instalados 17 arquivos Frontend, incluindo Largest.
Somente esse texto passa a Ford Fusion Titanium AWD; append e troca de ponteiro
preservam demais bytes do chunk, charset e todos os outros chunks/textos.
Labels não foi modificado. Nome instalado junto do segundo teste, confirmação
visual pendente. REWARD_NAME_097 em Global menciona Mustang, mas foi deixado
intacto por ser descrição de recompensa, e não o nome principal do carro.

Scripts locais recusam instalar com NFSC aberto, verificam hashes de backup,
candidata e destino e não sobrescrevem alterações posteriores desconhecidas.
Backup de GLOBAL em work/global-before-integration-2018; idiomas em
work/languages-before-integration-2018. Restore recupera arquivos originais.
Nenhuma nova release publicada. Próximos: confirmar direção/nome, logotipo Fusion;
depois port do 2012 FWD no CAMARO. ON de freio e faixas originais continuam
melhorias pendentes no TODO, sem reabrir o acabamento visual aprovado.

Fontes: [Attribulator 2.0](https://github.com/NFSTools/Attribulator/releases/tag/v2.0.0),
[ModScript](https://nfs-tools.blogspot.com/2018/02/nfs-vlted-usage-2-modscript-format.html),
[Labrune, formato de idiomas](https://github.com/nlgxzef/Labrune).
