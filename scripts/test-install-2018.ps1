param([ValidateSet('Install','Restore')][string]$Action = 'Install',
      [string]$GameRoot = 'D:\Program Files (x86)\Electronic Arts\Need for Speed Carbon')
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$gameFolder = Join-Path $GameRoot 'CARS/MUSTANGGT'
$backupFolder = Join-Path $GameRoot 'CARS/MUSTANGGT_backup_stock'
$referenceFolder = Join-Path $repoRoot 'reference/carbon-stock/MUSTANGGT'
if (Get-Process -Name NFSC -ErrorAction SilentlyContinue) { throw 'Feche o jogo antes de instalar/restaurar.' }
if ($Action -eq 'Install') {
    $verification = Get-Content (Join-Path $repoRoot 'docs/carbon2018-stage-axes-verification.json') -Raw | ConvertFrom-Json
    if (-not $verification.passed) { throw 'Auditoria corrigida não aprovada.' }
    foreach ($file in $verification.files) {
        if ((Get-FileHash -LiteralPath (Join-Path $repoRoot $file.path)).Hash -ne $file.sha256) { throw 'Staging mudou após auditoria.' }
    }
}
if ($Action -eq 'Install' -and -not (Test-Path -LiteralPath $backupFolder)) {
    foreach ($name in @('GEOMETRY.BIN','TEXTURES.BIN','VINYLS.BIN')) {
        if ((Get-FileHash -LiteralPath (Join-Path $gameFolder $name)).Hash -ne
            (Get-FileHash -LiteralPath (Join-Path $referenceFolder $name)).Hash) { throw 'Instalação não corresponde à referência preservada.' }
    }
    Copy-Item -LiteralPath $gameFolder -Destination $backupFolder -Recurse
}
foreach ($name in @('GEOMETRY.BIN','TEXTURES.BIN','VINYLS.BIN')) {
    if ((Get-FileHash -LiteralPath (Join-Path $backupFolder $name)).Hash -ne
        (Get-FileHash -LiteralPath (Join-Path $referenceFolder $name)).Hash) { throw 'Backup difere da referência.' }
}
$vinylHash = (Get-FileHash -LiteralPath (Join-Path $gameFolder 'VINYLS.BIN')).Hash
foreach ($name in @('GEOMETRY.BIN','TEXTURES.BIN')) {
    $sourceFolder = if ($Action -eq 'Restore') { $backupFolder } else { Join-Path $repoRoot 'work/carbon2018-stage-axes' }
    $source = Join-Path $sourceFolder $name
    $target = Join-Path $gameFolder $name
    Copy-Item -LiteralPath $source -Destination $target
    if ((Get-FileHash -LiteralPath $target).Hash -ne (Get-FileHash -LiteralPath $source).Hash) { throw 'Hash após cópia difere.' }
}
if ((Get-FileHash -LiteralPath (Join-Path $gameFolder 'VINYLS.BIN')).Hash -ne $vinylHash) { throw 'VINYLS mudou inesperadamente.' }
$state = [ordered]@{ action=$Action; time=[DateTimeOffset]::Now.ToString('o'); slot='MUSTANGGT'; backup=$backupFolder;
    geometry=(Get-FileHash -LiteralPath (Join-Path $gameFolder 'GEOMETRY.BIN')).Hash;
    textures=(Get-FileHash -LiteralPath (Join-Path $gameFolder 'TEXTURES.BIN')).Hash;
    vinyls=$vinylHash; status='experimental test only; VLT/FE unchanged' }
$state | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $repoRoot 'docs/carbon2018-test-install.json') -Encoding utf8
Write-Output "$Action concluído; backup verificado; somente GEOMETRY/TEXTURES do MUSTANGGT alterados."
