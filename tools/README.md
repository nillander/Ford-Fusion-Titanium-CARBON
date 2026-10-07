# Toolchain

`vendor/mw/` é uma cópia local ignorada no Git de utilitários do projeto MW:
mwgc.exe, mwtc.exe, RetargetSlot.exe e o fonte RetargetSlot.cs.
Origens e SHA-256 estão em `toolchain-manifest.json`.

Esses executáveis são **MW**, não um exportador Carbon. RetargetSlot apenas
renomeia sólidos/hashes em geometry MW. Não utilizá-lo para converter formatos.

Leitores de referência Carbon disponíveis no projeto irmão:
`../fusion-mw2005/tools/NFS-ModTools/Common/Geometry/CarbonSolidReader.cs` e
`CarbonSolidListReader.cs`. A descompressão CIP depende de CompLib.

Binary, VltEd e um exportador Carbon ainda precisam ser localizados/preparados.
Não copiar a toolchain inteira sem necessidade; manter as licenças dos projetos
de origem ao redistribuir qualquer ferramenta. Os executáveis não entram na release.
