param(
    [string]$MwRoot = 'C:\Users\nillander\NoDocuments\fusion-mw2005',
    [string]$CarbonRoot = 'D:\Program Files (x86)\Electronic Arts\Need for Speed Carbon'
)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$manifest = [System.Collections.Generic.List[object]]::new()
foreach ($folder in 'source','tools','versions','release','docs','capturas','work','reference') {
    New-Item -ItemType Directory -Path (Join-Path $repoRoot $folder) -Force | Out-Null
}
function Record-File($Path, $Origin, $Role) {
    $manifest.Add([ordered]@{
        path = [IO.Path]::GetRelativePath($repoRoot, $Path).Replace('\','/')
        origin = $Origin
        role = $Role
        bytes = (Get-Item -LiteralPath $Path).Length
        sha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
    })
}
$packages = @(
    @{name='Fusion2012_FWD_MW2005';hash='FAF2EC7BBF3AF4CDF169CB9086163FDA8AE855D2C3C4916E162546DB4531987D'},
    @{name='Fusion2018_AWD_MW2005';hash='D786292C56092EEFAC98E4CAB19E1A7D16A1B15A4B9D367D5B6C76A1F9D51E71'}
)
foreach ($package in $packages) {
    $zip = Join-Path $MwRoot ('release/' + $package.name + '.zip')
    if ((Get-FileHash -LiteralPath $zip).Hash -ne $package.hash) { throw "ZIP diferente da v2.8: $zip" }
    $destination = Join-Path $repoRoot ('reference/mw-v28/' + $package.name)
    Expand-Archive -LiteralPath $zip -DestinationPath $destination -Force
    foreach ($file in Get-ChildItem -LiteralPath $destination -File -Recurse) {
        Record-File $file.FullName $zip 'mw-v2.8'
    }
}
# O Backup instalado só contém localização; não comprova origem vanilla dos carros.
foreach ($slot in 'CAMARO','MUSTANGGT') {
    $destination = Join-Path $repoRoot ('reference/carbon-stock/' + $slot)
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    foreach ($name in 'GEOMETRY.BIN','TEXTURES.BIN','VINYLS.BIN') {
        $origin = Join-Path $CarbonRoot ('CARS/' + $slot + '/' + $name)
        $target = Join-Path $destination $name
        if (Test-Path -LiteralPath $target) {
            if ((Get-FileHash -LiteralPath $target).Hash -ne (Get-FileHash -LiteralPath $origin).Hash) {
                throw "Referencia preservada difere do jogo: $target. Não sobrescrever doador sem revisar."
            }
        } else { Copy-Item -LiteralPath $origin -Destination $target }
        Record-File $target $origin 'carbon-installed-donor-unverified-stock'
    }
}
$globalDestination = Join-Path $repoRoot 'reference/carbon-global-before'
New-Item -ItemType Directory -Path $globalDestination -Force | Out-Null
foreach ($file in Get-ChildItem -LiteralPath (Join-Path $CarbonRoot 'GLOBAL') -File) {
    $target = Join-Path $globalDestination $file.Name
    if (Test-Path -LiteralPath $target) {
        if ((Get-FileHash -LiteralPath $target).Hash -ne (Get-FileHash -LiteralPath $file.FullName).Hash) {
            throw "Backup GLOBAL preservado difere do jogo: $target"
        }
    } else { Copy-Item -LiteralPath $file.FullName -Destination $target }
    Record-File $target $file.FullName 'carbon-global-before'
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $repoRoot 'docs/reference-manifest.json') -Encoding utf8
Write-Output "Referencias preparadas: $($manifest.Count) arquivos; nenhum arquivo do jogo alterado."
