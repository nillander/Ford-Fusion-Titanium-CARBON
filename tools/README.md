# Toolchain

`vendor/mw/` é uma cópia local ignorada no Git de utilitários do projeto MW:
mwgc.exe, mwtc.exe, RetargetSlot.exe e o fonte RetargetSlot.cs.
Origens e SHA-256 estão em `toolchain-manifest.json`.

Esses executáveis são **MW**, não um exportador Carbon. RetargetSlot apenas
renomeia sólidos/hashes em geometry MW. Não utilizá-lo para converter formatos.

Leitores de referência Carbon disponíveis no projeto irmão:
`../fusion-mw2005/tools/NFS-ModTools/Common/Geometry/CarbonSolidReader.cs` e
`CarbonSolidListReader.cs`. A descompressão CIP depende de CompLib.

## Ferramentas Carbon obtidas

- CarToolkit 3.1: `vendor/cartoolkit/app/NFS-CarToolkit/NFS-CarToolkit.exe`.
  [Autor](https://nfs-tools.blogspot.com/2020/07/nfs-cartoolkit-v31-released.html).
  `cartoolkit.7z` e `vlted.7z` (4.6, extraído em `vendor/cartoolkit/vlted/` com 7-Zip 24.09 por causa do filtro BCJ2) vieram do link MEGA
  alternativo na [página oficial](https://nfs-tools.blogspot.com/p/downloads.html):
  https://mega.nz/folder/GahkUB6B#vB1Cpy7PeUfe9O7FetG2Ag.
- Carbon ModTools 1.1: `vendor/carbon-modtools/NFS Carbon ModTools v1.1/bin/`.
  [Documentação do autor](https://nfs-tools.blogspot.com/2010/05/nfscarbon-modtools-v10-released.html),
  arquivo distribuído em https://nfs.com.ru/downloads/1404. Preservar licença/readme.
  O exemplo Bugatti serviu apenas de documentação, nunca de doador.
- QuickBMS 0.12.0: `vendor/quickbms/quickbms.exe`, pacote do autor
  https://mirror.aluigi.org/papers/quickbms.zip. Decoder HUFF/EA com script próprio
  `scripts/decode-huff.bms`; CIP/JDLZ tratados no extrator PS.
- meshoptimizer 1.3.0 (MIT): `vendor/meshoptimizer/package/`, tarball npm
  https://registry.npmjs.org/meshoptimizer/-/meshoptimizer-1.3.0.tgz.
  [API oficial](https://github.com/zeux/meshoptimizer/blob/master/js/README.md).
- megajs 1.3.10 (MIT): `vendor/megajs/package/`, tarball npm
  https://registry.npmjs.org/megajs/-/megajs-1.3.10.tgz.
  [Documentação](https://mega.js.org/). Usado para baixar a pasta pública do autor.
- UPX 5.2.1 usado apenas para inspecionar uma cópia do nfscgc em work;
  executáveis distribuídos intactos. Não é dependência de reprodução.

SHA-256 no manifesto. Dependências: Python/numpy 1.26.4, Node, PowerShell7 e
Validator.dll do projeto MW (leitores NFS-ModTools). Comandos na passagem do Claude.
Manter as licenças de origem. Nenhum executável de terceiro entra na release.
