# Integração do Fusion 2018 — 07/10/2026

## Histórico das duas primeiras candidatas

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

## Continuação: direção, fogo e logotipo (17:18)

Usuário confirmou o nome, rejeitou a segunda direção e enviou imagem do fogo
abaixo das ponteiras; logotipo ainda Mustang GT. Nome agora concluído no TODO.

Terceira direção: DIFFERENTIAL 0,35/0,5/0,5, grip dianteiro/traseiro equilibrado,
YAW_CONTROL original do doador, YAW_SPEED 0,3. Mantém AWD 0,5, preço 50.000 e
curva de ângulo +15%. Isso é hipótese de acerto, não diagnóstico conclusivo.
Segunda candidata preservada em work/global2018-performance-second e gate
carbon2018-performance-second-verification.json. Nova conversão: 74 campos,
11 nós; 10.180 nós/312 blobs auditados; rollback compilado de novo e comparado
semanticamente com os originais. SHA atual 547C601A….

ModScript agora escreve também valores iguais à base original, para restaurar
STEERING/YAW_CONTROL ao importar sobre versões anteriores. Aplicação sobre a
segunda candidata produziu hash binário diferente, mas a auditoria completa
confirmou todos os nós/blobs semanticamente idênticos à terceira candidata.
Rollback novo foi aplicado sobre esse resultado e novamente validado.

Fogo: medição BASE_A/material cromado nas saídas traseiras: Z 0,114224..0,240455 m,
centro 0,177339 m. EXHAUST estava em 0,135 m. Hash oficial explícito 66A4A9DE;
o hash calculado de EXHAUST não o encontra. Somente quatro bytes de translação
Z por marcador: 60 pontos em 30 BODY; outras 160 peças exatas. 190 malhas
validadas e streams JDLZ com flags finais conferidos. GEOMETRY 4C8CFDF9….

Logo: FRONTB1.BUN primeira TPK inclui SECONDARY_LOGO_MUSTANGGT, hash 710ABB50,
256×64, formato D3D 21 ARGB8888 (um mip), 65.536 bytes. FrontB1.lzc originalmente
descomprime para BUN idêntico. Arte Fusion existente no SECONDARYLOGO.BIN MW
é DXT3; pixels decodificados/convertidos para BGRA, mantendo o header Carbon.
Outros bytes do BUN idênticos e LZC recompresso equivalente. Leitor independente
valida 264 texturas; opção AllowArgb8888 adicionada sem afrouxar o padrão DXT.
Prévia de conversão e imagem do problema preservadas em docs/imagens/integracao-2018.

Verificador reproduzível verify-corrections-2018.py exige o escopo das diferenças
e executa leitores independentes antes de marcar os gates aprovados. Novo
instalador de quatro arquivos com preflight/hashes/backup transacional/rollback
automático em falha. Instalado às 17:18 com NFSC/VltEd fechados. Nome/idiomas,
TEXTURES/VINYLS, FE_ATTRIB e outros slots não tocados nessa rodada.

Pergunta de QA enviada: curvas em baixa velocidade/corrida, fogo e logo no menu.
Ainda sem resposta. Não marcar essas três correções como aprovadas no jogo.
Nova release não publicada; próxima fase 2012 continua aguardando essa aprovação.

## Aprovação, motor e release v1.2

Usuário: "tudo certo" para direção, logo e fogo; autorizou commit/push/tag/release.
Também pediu potência 20% acima da BMW M3 GTR. Identificada a referência pelo
pvehicle jogável bmwm3gtre46; engine bmwm3gtr existe mas não é referenciado ali.
Base/top do Fusion usam TORQUE original BMW ×1,20 e limites BMW 9500/8500 RPM.
Indução/nitro preservados; declarar curva do motor +20%, não velocidade +20%.

Novo attributes D58BEA8A… instalado. Direção/tração/preço mantidos; plano novo
difere do aprovado somente em TORQUE/MAX_RPM/RED_LINE dos dois nós de motor.
Todos os 10.180 nós/312 blobs conferidos; importação sobre segunda candidata
equivalente e rollback validado. Novo motor ainda não foi retestado em corrida.
Backup da aprovação anterior e gate preservados.

Pacote v1.2 incorpora todos os 22 arquivos necessários à instalação completa,
com ModScripts para integração manual de performance. Guarda o estado anterior
e recusa outras versões/mods por hash antes de escrever; cópia é transacional.
Testes reais do script no Windows PowerShell 5.1: ZIP/checksums, instalação,
reinstalação, restauração e rejeição sem alterações de pacote/destino modificado.
SHA-256 ZIP em local/release-v1.2/SHA256SUMS.txt; gate docs/release-v1.2-verification.json.
README, TODO, handoff e notas de release atualizados; publicação autorizada.
