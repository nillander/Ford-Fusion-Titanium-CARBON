param([string]$ReaderAssembly = 'C:\Users\nillander\NoDocuments\fusion-mw2005\scripts\validator\bin\Release\net8.0\Validator.dll',
      [string]$InputRoot = 'work/carbon-solids',
      [string]$OutputFile = 'docs/carbon-mesh-audit.json',
      [switch]$AllowEmptySentinel)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Add-Type -Path $ReaderAssembly
$references = @((Get-ChildItem (Join-Path $PSHOME 'ref') -Filter '*.dll').FullName) + $ReaderAssembly
Add-Type -ReferencedAssemblies $references -IgnoreWarnings -WarningAction SilentlyContinue -TypeDefinition @'
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text.Json;
using Common.Geometry;
using Common.Geometry.Data;
public static class CarbonAudit {
 public static void Run(string root, string destination, bool allowEmptySentinel) {
  var records = new List<object>();
  foreach (string file in Directory.GetFiles(root,"*.bin",SearchOption.AllDirectories).OrderBy(p=>p)) {
   using var br = new BinaryReader(File.OpenRead(file));
   br.BaseStream.Position=8;
   CarbonObject s;
   try { s = new CarbonSolidReader().Read(br,(uint)(br.BaseStream.Length-8)); }
   catch (Exception e) { throw new Exception("Reader failed on " + file, e); }
   if (s.Materials.Count==0 || s.VertexSets.Count==0) {
    if (allowEmptySentinel && s.Hash==0 && s.Name=="" && s.Materials.Count==0 && s.VertexSets.Sum(v=>v.Count)==0) {
     records.Add(new { name="", hash="00000000", emptySentinel=true });
     Console.WriteLine("WARNING: empty compiler sentinel; exclude before release"); continue;
    }
    throw new Exception("Empty mesh: "+s.Name);
   }
   int tris=0;
   foreach(var m in s.Materials) {
    var vertices=s.VertexSets[m.VertexSetIndex];
    if(m.Indices.Length%3!=0 || m.Indices.Any(i=>i>=vertices.Count)) throw new Exception("Invalid indices: "+s.Name);
    foreach(var v in vertices) {
     if(!float.IsFinite(v.Position.X)||!float.IsFinite(v.Position.Y)||!float.IsFinite(v.Position.Z)||
        !float.IsFinite(v.TexCoords.X)||!float.IsFinite(v.TexCoords.Y)) throw new Exception("Nonfinite vertex: "+s.Name);
    }
    tris+=m.Indices.Length/3;
   }
   records.Add(new {name=s.Name,hash=s.Hash.ToString("X8"),vertices=s.VertexSets.Sum(v=>v.Count),
    triangles=tris, morphTargets=s.MorphTargets==null ? Array.Empty<string>() : s.MorphTargets.Select(h=>h.ToString("X8")).ToArray(),
    min=new[]{s.MinPoint.X,s.MinPoint.Y,s.MinPoint.Z},max=new[]{s.MaxPoint.X,s.MaxPoint.Y,s.MaxPoint.Z},
    materials=s.Materials.Select(m=>new {m.Name,m.Flags,effect=((CarbonMaterial)m).EffectId,
     diffuse=m.DiffuseTextureHash.ToString("X8"),normal=m.NormalTextureHash?.ToString("X8"),
     specular=m.SpecularTextureHash?.ToString("X8"),vertices=m.NumVerts,indices=m.Indices.Length})});
  }
  File.WriteAllText(destination,JsonSerializer.Serialize(records,new JsonSerializerOptions{WriteIndented=true})+"\n");
  Console.WriteLine("Independent Carbon mesh read passed: "+records.Count+" solids");
 }
}
'@
[CarbonAudit]::Run((Join-Path $repoRoot $InputRoot),(Join-Path $repoRoot $OutputFile),$AllowEmptySentinel.IsPresent)
