param([string]$InputRoot = 'work/carbon2018-stage-axes-solids',
      [string]$OutputFile = 'docs/carbon2018-vertex-attributes.json')
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$assembly = Join-Path (Split-Path $repoRoot -Parent) 'fusion-mw2005/scripts/validator/bin/Release/net8.0/Validator.dll'
Add-Type -Path $assembly
$references = @((Get-ChildItem (Join-Path $PSHOME 'ref') -Filter '*.dll').FullName) + $assembly
Add-Type -ReferencedAssemblies $references -IgnoreWarnings -WarningAction SilentlyContinue -TypeDefinition @'
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using Common.Geometry;
public static class AttributeAudit {
 public static void Run(string root, string output) {
  var report = new List<object>();
  foreach(var file in Directory.GetFiles(root,"*.bin",SearchOption.AllDirectories)) {
   using var br = new BinaryReader(File.OpenRead(file)); br.BaseStream.Position=8;
   var s = new CarbonSolidReader().Read(br,(uint)(br.BaseStream.Length-8));
   var vertices=s.VertexSets.SelectMany(v=>v).ToArray();
   report.Add(new {name=s.Name, colors=vertices.GroupBy(v=>v.Color).Select(g=>new{color=g.Key?.ToString("X8"),count=g.Count()}),
    nonfiniteNormals=vertices.Count(v=>v.Normal.HasValue && (!float.IsFinite(v.Normal.Value.X)||!float.IsFinite(v.Normal.Value.Y)||!float.IsFinite(v.Normal.Value.Z))),
    zeroNormals=vertices.Count(v=>!v.Normal.HasValue||v.Normal.Value.LengthSquared()<1e-10f),
    nonunitNormals=vertices.Count(v=>v.Normal.HasValue && Math.Abs(v.Normal.Value.Length()-1)>0.01f),
    nonfiniteTangents=vertices.Count(v=>v.Tangent.HasValue && (!float.IsFinite(v.Tangent.Value.X)||!float.IsFinite(v.Tangent.Value.Y)||!float.IsFinite(v.Tangent.Value.Z))),
    zeroTangents=vertices.Count(v=>v.Tangent.HasValue && v.Tangent.Value.LengthSquared()<1e-10f),
    samples=vertices.Take(3).Select(v=>new{p=new[]{v.Position.X,v.Position.Y,v.Position.Z},uv=new[]{v.TexCoords.X,v.TexCoords.Y},color=v.Color?.ToString("X8")})});
  }
  File.WriteAllText(output,JsonSerializer.Serialize(report,new JsonSerializerOptions{WriteIndented=true})+"\n");
  Console.WriteLine("Audited vertex attributes of "+report.Count+" solids");
 }
}
'@
[AttributeAudit]::Run((Join-Path $repoRoot $InputRoot),(Join-Path $repoRoot $OutputFile))
