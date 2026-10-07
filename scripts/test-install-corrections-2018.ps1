param(
    [ValidateSet('Install','Restore')][string]$Action = 'Install',
    [string]$GamePath = 'D:\Program Files (x86)\Electronic Arts\Need for Speed Carbon'
)
$ErrorActionPreference = 'Stop'
$projectPath = Split-Path $PSScriptRoot -Parent
if (Get-Process NFSC,NFS-VltEd -ErrorAction SilentlyContinue) { throw 'Feche NFSC e VltEd antes de instalar/restaurar.' }
$performance = Get-Content (Join-Path $projectPath 'docs/carbon2018-performance-verification.json') -Raw | ConvertFrom-Json
$geometry = Get-Content (Join-Path $projectPath 'docs/carbon2018-stage-exhaust-verification.json') -Raw | ConvertFrom-Json
$logo = Get-Content (Join-Path $projectPath 'docs/carbon2018-frontend-logo-verification.json') -Raw | ConvertFrom-Json
if ($performance.status -ne 'passed' -or -not $performance.rollback_semantically_identical -or -not $geometry.passed -or -not $logo.passed) { throw 'Auditorias incompletas.' }
$operations = @(
    @{ destination='GLOBAL/attributes.bin'; candidate='work/global2018-performance/main/attributes.bin'; backup='work/global2018-performance-second/main/attributes.bin'; expected=$performance.attributes_sha256; before=$performance.second_candidate_attributes_sha256 },
    @{ destination='CARS/MUSTANGGT/GEOMETRY.BIN'; candidate='work/carbon2018-stage-exhaust/GEOMETRY.BIN'; backup='work/carbon2018-stage-roof/GEOMETRY.BIN'; expected=($geometry.files | Where-Object path -Like '*/GEOMETRY.BIN').sha256; before='DE8EE10F8DDA430076D15CAD4DA796398B5BC85DC2EC9D33B4B6B1F94967680E' }
)
foreach ($file in $logo.files) {
    $operations += @{ destination="FRONTEND/$($file.name)"; candidate=$file.path; backup="work/frontend-before-logo-2018/$($file.name)"; expected=$file.sha256; before=$file.backup_sha256 }
}
# Preflight every file before writing anything. Restore recovers the previous
# local test (v1.1 geometry + second handling comparison + original logo).
foreach ($op in $operations) {
    $op.candidate = Join-Path $projectPath $op.candidate
    $op.backup = Join-Path $projectPath $op.backup
    $op.destination = Join-Path $GamePath $op.destination
    if ((Get-FileHash -LiteralPath $op.candidate).Hash -ne $op.expected) { throw 'Candidata mudou após auditoria.' }
    if ((Get-FileHash -LiteralPath $op.backup).Hash -ne $op.before) { throw 'Backup mudou.' }
    $current = (Get-FileHash -LiteralPath $op.destination).Hash
    $known = @($op.expected,$op.before)
    if ($op.destination -eq (Join-Path $GamePath 'GLOBAL/attributes.bin')) { $known += $performance.approved_handling_attributes_sha256 }
    if ($current -notin $known) { throw "Destino alterado por outro processo: $($op.destination)" }
}
$transaction = Join-Path $projectPath ('work/corrections-install-transaction-'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $transaction | Out-Null
for ($i=0; $i -lt $operations.Count; $i++) {
    Copy-Item -LiteralPath $operations[$i].destination -Destination (Join-Path $transaction "$i.bin")
}
try {
    foreach ($op in $operations) {
        $source = if ($Action -eq 'Install') { $op.candidate } else { $op.backup }
        Copy-Item -LiteralPath $source -Destination $op.destination -Force
        if ((Get-FileHash -LiteralPath $op.destination).Hash -ne (Get-FileHash -LiteralPath $source).Hash) { throw 'Hash instalado divergente.' }
    }
} catch {
    for ($i=0; $i -lt $operations.Count; $i++) {
        Copy-Item -LiteralPath (Join-Path $transaction "$i.bin") -Destination $operations[$i].destination -Force
    }
    throw
}
$manifest = [ordered]@{
    action=$Action; installed_at=(Get-Date).ToString('o'); game_validation='pending'; transaction_backup=$transaction
    files=@($operations | ForEach-Object { @{path=$_.destination; sha256=(Get-FileHash -LiteralPath $_.destination).Hash} })
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $projectPath 'docs/carbon2018-corrections-install.json') -Encoding utf8
Write-Output "$Action concluído: direção candidata, pontos EXHAUST e logotipo Fusion."
