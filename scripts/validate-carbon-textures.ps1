param([string]$ReaderAssembly = 'C:\Users\nillander\NoDocuments\fusion-mw2005\scripts\validator\bin\Release\net8.0\Validator.dll',
      [string]$InputFile = 'work/carbon2018-stage/TEXTURES.BIN',
      [string]$OutputFile = 'docs/carbon2018-texture-audit.json')
$ErrorActionPreference = 'Stop'
Add-Type -Path $ReaderAssembly
. (Join-Path $PSScriptRoot 'extract-carbon-solids.ps1') -LibraryOnly
$references = @((Get-ChildItem (Join-Path $PSHOME 'ref') -Filter '*.dll').FullName) + $ReaderAssembly
$readerSource = Get-Content 'C:\Users\nillander\NoDocuments\fusion-mw2005\tools\NFS-ModTools\Common\Textures\Version3Tpk.cs' -Raw
$readerSource = $readerSource.Replace('namespace Common.Textures', 'namespace CarbonValidation').Replace(': TpkManager', ': Common.Textures.TpkManager').Replace('Compression.DecompressCip', 'CarbonTextureCip.Decompress')
$auditSource = @'
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text.Json;
using Common;
using Common.Textures.Data;
public static class CarbonTextureCip {
 public static Func<byte[],byte[]> Decode;
 public static long Decompress(Stream input,Stream output,long length) {
  var packed=new byte[checked((int)length)]; input.ReadExactly(packed);
  var result=Decode(packed); output.Write(result); return result.Length;
 }
}
public static class CarbonTextureAudit {
 public static void Run(string file, string destination) {
  using var br=new BinaryReader(File.OpenRead(file));
  if(br.ReadUInt32()!=0xB3300000)throw new Exception("Unexpected TPK container");
  var textures=new CarbonValidation.Version3Tpk().ReadTexturePack(br,br.ReadUInt32()).Textures;
  if(textures.Count==0)throw new Exception("No textures parsed");
  if(textures.Select(t=>t.TexHash).Distinct().Count()!=textures.Count)throw new Exception("Duplicate texture hash");
  foreach(var t in textures) {
   if(t.Name.Length>23)throw new Exception("Texture name exceeds 23 characters: "+t.Name);
   if(t.Width==0||t.Height==0||t.Data.Length!=t.DataSize)throw new Exception("Invalid texture dimensions/data");
   if(t.Format!=0x31545844&&t.Format!=0x33545844&&t.Format!=0x35545844)throw new Exception("Unsupported DXT format");
   long required=0; long w=t.Width,h=t.Height;
   if(t.MipMapCount==0)throw new Exception("No mip levels");
   for(int i=0;i<t.MipMapCount;i++) {
    required+=(long)((w+3)/4)*((h+3)/4)*(t.Format==0x31545844?8:16);
    w=Math.Max(1,w/2); h=Math.Max(1,h/2);
   }
   if(t.DataSize<required)throw new Exception("Incomplete mip chain: "+t.Name);
  }
  File.WriteAllText(destination,JsonSerializer.Serialize(new{passed=true,count=textures.Count,textures=textures.Select(t=>new{t.Name,hash=t.TexHash.ToString("X8"),t.Width,t.Height,t.DataSize,t.MipMapCount,t.Format})},new JsonSerializerOptions{WriteIndented=true})+"\n");
  Console.WriteLine("Independent Carbon TPK read passed: "+textures.Count+" textures");
 }
}
'@
Add-Type -ReferencedAssemblies $references -IgnoreWarnings -WarningAction SilentlyContinue -TypeDefinition ($auditSource + $readerSource.Replace('using System;', '').Replace('using System.Collections.Generic;', '').Replace('using System.IO;', '').Replace('using System.Runtime.InteropServices;', '').Replace('using Common.Textures.Data;', ''))
[CarbonTextureCip]::Decode = [Func[byte[],byte[]]] {
    param($packed)
    $cursor = 0
    $size = 0
    while ($cursor -lt $packed.Length) {
        if ($cursor + 24 -gt $packed.Length) { throw 'Truncated CIP header' }
        $blockSize = [BitConverter]::ToInt32($packed,$cursor+8)
        if ($blockSize -lt 40 -or $blockSize -gt $packed.Length-$cursor) { throw 'Invalid CIP block' }
        $size = [Math]::Max($size, [BitConverter]::ToInt32($packed,$cursor+12)+[BitConverter]::ToInt32($packed,$cursor+4))
        $cursor += $blockSize
    }
    return ,[CarbonCip]::Extract($packed,0,$packed.Length,$size,$decoder)
}
[CarbonTextureAudit]::Run((Resolve-Path $InputFile).Path, [IO.Path]::GetFullPath($OutputFile))
