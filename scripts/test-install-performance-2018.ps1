param(
    [ValidateSet('Install','Restore')][string]$Action = 'Install',
    [string]$GamePath = 'D:\Program Files (x86)\Electronic Arts\Need for Speed Carbon'
)
$ErrorActionPreference = 'Stop'
$projectPath = Split-Path $PSScriptRoot -Parent
if (Get-Process NFSC -ErrorAction SilentlyContinue) { throw 'Feche NFSC antes de instalar/restaurar.' }
if (Get-Process NFS-VltEd -ErrorAction SilentlyContinue) { throw 'Feche VltEd para evitar Save de dados antigos.' }
$gatePath = Join-Path $projectPath 'docs/carbon2018-performance-verification.json'
$gate = Get-Content -LiteralPath $gatePath -Raw | ConvertFrom-Json
if ($gate.status -ne 'passed' -or -not $gate.rollback_semantically_identical) { throw 'Auditoria incompleta.' }
$backupPath = Join-Path $projectPath 'work/global-before-integration-2018/attributes.bin'
$candidatePath = Join-Path $projectPath 'work/global2018-performance/main/attributes.bin'
$installedPath = Join-Path $GamePath 'GLOBAL/attributes.bin'
if ((Get-FileHash -LiteralPath $backupPath).Hash -ne $gate.backup_attributes_sha256) { throw 'Backup divergente.' }
if ((Get-FileHash -LiteralPath $candidatePath).Hash -ne $gate.attributes_sha256) { throw 'Candidata divergente.' }
$currentHash = (Get-FileHash -LiteralPath $installedPath).Hash
if ($currentHash -notin @($gate.backup_attributes_sha256, $gate.attributes_sha256, $gate.previous_candidate_attributes_sha256, $gate.second_candidate_attributes_sha256, $gate.approved_handling_attributes_sha256)) { throw 'GLOBAL foi alterado depois do backup. Não sobrescrever.' }
$sourcePath = if ($Action -eq 'Install') { $candidatePath } else { $backupPath }
$expectedHash = (Get-FileHash -LiteralPath $sourcePath).Hash
Copy-Item -LiteralPath $sourcePath -Destination $installedPath -Force
if ((Get-FileHash -LiteralPath $installedPath).Hash -ne $expectedHash) { throw 'Hash instalado divergente.' }
$manifest = [ordered]@{
    action = $Action; installed_at = (Get-Date).ToString('o'); attributes_sha256 = $expectedHash
    game_path = $GamePath; only_file_changed = 'GLOBAL/attributes.bin'; game_validation = 'pending'
}
$manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $projectPath 'docs/carbon2018-performance-install.json') -Encoding utf8
Write-Output "$Action concluído: attributes.bin $expectedHash"
