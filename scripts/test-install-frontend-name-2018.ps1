param(
    [ValidateSet('Install','Restore')][string]$Action = 'Install',
    [string]$GamePath = 'D:\Program Files (x86)\Electronic Arts\Need for Speed Carbon'
)
$ErrorActionPreference = 'Stop'
$projectPath = Split-Path $PSScriptRoot -Parent
if (Get-Process NFSC -ErrorAction SilentlyContinue) { throw 'Feche NFSC antes de instalar/restaurar idiomas.' }
$reportPath = Join-Path $projectPath 'docs/carbon2018-frontend-name-verification.json'
$report = Get-Content -LiteralPath $reportPath -Raw | ConvertFrom-Json
if ($report.status -ne 'passed' -or -not $report.only_record_changed) { throw 'Auditoria de idiomas incompleta.' }
$operations = foreach ($file in $report.files) {
    if ($file.file -ne [IO.Path]::GetFileName($file.file)) { throw 'Nome de arquivo inválido.' }
    $backupPath = Join-Path $projectPath "work/languages-before-integration-2018/$($file.file)"
    $candidatePath = Join-Path $projectPath "work/languages2018-name/$($file.file)"
    $destinationPath = Join-Path $GamePath "LANGUAGES/$($file.file)"
    if ((Get-FileHash -LiteralPath $backupPath).Hash -ne $file.before_sha256) { throw 'Backup de idioma divergente.' }
    if ((Get-FileHash -LiteralPath $candidatePath).Hash -ne $file.after_sha256) { throw 'Candidata de idioma divergente.' }
    $currentHash = (Get-FileHash -LiteralPath $destinationPath).Hash
    if ($currentHash -notin @($file.before_sha256,$file.after_sha256)) { throw "Idioma alterado após backup: $($file.file)" }
    [pscustomobject]@{
        Source = $(if ($Action -eq 'Install') { $candidatePath } else { $backupPath })
        Destination = $destinationPath
        Expected = $(if ($Action -eq 'Install') { $file.after_sha256 } else { $file.before_sha256 })
    }
}
# Validate every file before copying any file.
foreach ($operation in $operations) {
    Copy-Item -LiteralPath $operation.Source -Destination $operation.Destination -Force
    if ((Get-FileHash -LiteralPath $operation.Destination).Hash -ne $operation.Expected) { throw 'Idioma instalado divergente.' }
}
$report.installed = $Action -eq 'Install'
$report.game_validation = 'pending'
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding utf8
Write-Output "$Action concluído: $($operations.Count) idiomas; nome Ford Fusion Titanium AWD."
