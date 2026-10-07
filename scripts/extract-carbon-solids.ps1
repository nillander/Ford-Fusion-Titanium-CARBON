param([string]$JdlzSource = 'C:\Users\nillander\NoDocuments\fusion-mw2005\tools\OpenNFSTools\LibNFS\Compression\JDLZ.cs',
      [string]$InventoryFile = 'docs/geometry-inventory.json',
      [string]$OutputRoot = 'work/carbon-solids',
      [switch]$LibraryOnly)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$script:huffFolder = Join-Path $repoRoot 'work/huff-decode'
$script:huffTool = Join-Path $repoRoot 'tools/vendor/quickbms/quickbms.exe'
$script:huffScript = Join-Path $PSScriptRoot 'decode-huff.bms'
New-Item -ItemType Directory -Path $script:huffFolder -Force | Out-Null
Add-Type -Path $JdlzSource
# CIP's 24-byte block header stores unpacked size, packed size and output offset.
# Large solids store blocks out of order; append-only extraction corrupts them.
Add-Type -TypeDefinition @'
using System;
using System.IO;
public static class CarbonCip {
 public static byte[] Extract(byte[] file, int offset, int packedSize, int unpackedSize,
                             Func<byte[], byte[]> decode) {
  var output = new byte[unpackedSize];
  var covered = new bool[unpackedSize];
  int end = checked(offset + packedSize);
  if (offset < 0 || end > file.Length) throw new InvalidDataException("CIP extent");
  while (offset < end) {
   if (offset + 40 > end || BitConverter.ToUInt32(file, offset) != 0x55441122)
    throw new InvalidDataException("CIP block header");
   int size = BitConverter.ToInt32(file, offset + 4);
   int packed = BitConverter.ToInt32(file, offset + 8);
   int destination = BitConverter.ToInt32(file, offset + 12);
   int blobLength = BitConverter.ToInt32(file, offset + 36);
   // HUFF stores payload length; JDLZ stores total blob length.
   if (file[offset+24] == 'H' && file[offset+25] == 'U' &&
       file[offset+26] == 'F' && file[offset+27] == 'F') blobLength += 16;
   if (packed < 40 || packed > end - offset || blobLength < 16 || blobLength > packed - 24 ||
       destination < 0 || size <= 0 || size > output.Length - destination)
    throw new InvalidDataException("CIP block bounds");
   var blob = new byte[blobLength];
   Buffer.BlockCopy(file, offset + 24, blob, 0, blobLength);
   var block = decode(blob);
   if (block.Length != size) throw new InvalidDataException("CIP size mismatch");
   for (int i = destination; i < destination + size; i++) {
    if (covered[i]) throw new InvalidDataException("CIP overlap");
    covered[i] = true;
   }
   Buffer.BlockCopy(block, 0, output, destination, size);
   offset += packed;
  }
  foreach (bool bit in covered) if (!bit) throw new InvalidDataException("CIP gap");
  return output;
 }
}
'@
$decoder = [Func[byte[],byte[]]] {
    param($blob)
    if ([Text.Encoding]::ASCII.GetString($blob,0,4) -eq 'RAWW') {
        $raw = [byte[]]::new($blob.Length - 16)
        [Array]::Copy($blob,16,$raw,0,$raw.Length)
        return ,$raw
    }
    if ([Text.Encoding]::ASCII.GetString($blob,0,4) -eq 'HUFF') {
        $inputPath = Join-Path $script:huffFolder 'input.huff'
        [IO.File]::WriteAllBytes($inputPath,$blob)
        $log = & $script:huffTool -o -Q $script:huffScript $inputPath $script:huffFolder 2>&1
        if ($LASTEXITCODE -ne 0) { throw "QuickBMS HUFF falhou: $log" }
        return ,[IO.File]::ReadAllBytes((Join-Path $script:huffFolder 'decoded.bin'))
    }
    [NFSTools.LibNFS.Compression.JDLZ]::decompress($blob)
}
if ($LibraryOnly) { return }
$inventories = Get-Content (Join-Path $repoRoot $InventoryFile) -Raw | ConvertFrom-Json
foreach ($catalogue in @($inventories | Where-Object { $_.streaming.Count -gt 0 })) {
    $slot = Split-Path (Split-Path $catalogue.path -Parent) -Leaf
    $inputPath = Join-Path $repoRoot $catalogue.path
    if ((Get-FileHash -LiteralPath $inputPath).Hash -ne $catalogue.sha256) { throw 'Hash de origem mudou' }
    $file = [IO.File]::ReadAllBytes($inputPath)
    $destination = Join-Path (Join-Path $repoRoot $OutputRoot) $slot
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    foreach ($entry in $catalogue.streaming) {
        if (-not $entry.compressed) { throw 'Este extrator espera CIP comprimido' }
        $solid = [CarbonCip]::Extract($file, $entry.offset, $entry.packed_bytes, $entry.bytes, $decoder)
        if ([BitConverter]::ToUInt32($solid,0) -ne [Convert]::ToUInt32('80134010',16) -or
            [BitConverter]::ToUInt32($solid,4) -ne ($solid.Length - 8) -or
            [BitConverter]::ToUInt32($solid,32) -ne [Convert]::ToUInt32($entry.hash,16)) {
            throw "Cabecalho/hash do solido difere: $($entry.hash); length=$($solid.Length); header=$([BitConverter]::ToString($solid,0,48))"
        }
        [IO.File]::WriteAllBytes((Join-Path $destination ($entry.hash + '.bin')), $solid)
    }
    Write-Output "$slot : $($catalogue.streaming.Count) solidos extraidos; tamanhos, cobertura CIP e hashes conferidos."
}
