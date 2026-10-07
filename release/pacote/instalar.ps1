param(
    [Parameter(Mandatory=$true)][string]$GamePath,
    [ValidateSet('Install','Restore')][string]$Action = 'Install'
)
$ErrorActionPreference = 'Stop'
function Get-PackageHash([string]$LiteralPath) {
    $stream = [IO.File]::OpenRead($LiteralPath)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { $digest = $algorithm.ComputeHash($stream) } finally { $stream.Dispose(); $algorithm.Dispose() }
    return [pscustomobject]@{Hash=[BitConverter]::ToString($digest).Replace('-','')}
}
if (Get-Process NFSC,NFS-VltEd -ErrorAction SilentlyContinue) { throw 'Feche NFSC e NFS-VltEd.' }
$gameRoot = [IO.Path]::GetFullPath($GamePath).TrimEnd('\','/')
if (-not (Test-Path -LiteralPath (Join-Path $gameRoot 'NFSC.exe'))) { throw 'Pasta sem NFSC.exe.' }
function Inside([string]$root,[string]$relative) {
    if ([IO.Path]::IsPathRooted($relative)) { throw 'Caminho absoluto no manifesto.' }
    $path = [IO.Path]::GetFullPath((Join-Path $root $relative))
    if (-not $path.StartsWith($root.TrimEnd('\','/')+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Caminho fora da pasta.' }
    return $path
}
$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'arquivos.json') -Raw | ConvertFrom-Json
if ($manifest.version -notmatch '^v[0-9]+[.][0-9]+$') { throw 'Versao invalida no manifesto.' }
$backupRoot = Join-Path $gameRoot ('Fusion2018_'+$manifest.version+'_backup')
$statePath = Join-Path $backupRoot 'estado.json'
$state = if (Test-Path -LiteralPath $statePath) { Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json } else { $null }
if ($Action -eq 'Restore' -and -not $state) { throw 'Backup desta release nao encontrado.' }
$operations = @()
foreach ($file in $manifest.files) {
    $source = Inside $PSScriptRoot $file.path
    $target = Inside $gameRoot $file.path
    $backup = Inside $backupRoot $file.path
    if ((Get-PackageHash -LiteralPath $source).Hash -ne $file.sha256) { throw "Pacote alterado: $($file.path)" }
    if (-not (Test-Path -LiteralPath $target)) { throw "Arquivo esperado ausente: $($file.path)" }
    $current = (Get-PackageHash -LiteralPath $target).Hash
    $before = $null
    if ($state) {
        $entry = @($state.files | Where-Object path -EQ $file.path)
        if ($entry.Count -ne 1) { throw 'Manifesto de backup incompleto.' }
        $before = $entry[0].sha256
        if ((Get-PackageHash -LiteralPath $backup).Hash -ne $before) { throw 'Backup alterado.' }
    }
    if ($current -notin (@($file.allowed_before)+@($file.sha256,$before))) {
        throw "Arquivo de outra versao/mod: $($file.path). Nenhum arquivo instalado. Use o ModScript para combinar outros mods."
    }
    $operations += [pscustomobject]@{path=$file.path;source=$source;target=$target;backup=$backup;current=$current;before=$before;after=$file.sha256}
}
# Validate the entire package and installation before creating the first backup.
if (-not $state) {
    foreach ($op in $operations) {
        New-Item -ItemType Directory -Path (Split-Path $op.backup -Parent) -Force | Out-Null
        Copy-Item -LiteralPath $op.target -Destination $op.backup -Force
        if ((Get-PackageHash -LiteralPath $op.backup).Hash -ne $op.current) { throw 'Falha no backup.' }
    }
    $state = [ordered]@{version=$manifest.version;files=@($operations | ForEach-Object { @{path=$_.path;sha256=$_.current} })}
    $state | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath $statePath -Encoding utf8
}
$transactionRoot = Join-Path $backupRoot ('transacao-'+[Guid]::NewGuid().ToString('N'))
foreach ($op in $operations) {
    $snapshot = Inside $transactionRoot $op.path
    New-Item -ItemType Directory -Path (Split-Path $snapshot -Parent) -Force | Out-Null
    Copy-Item -LiteralPath $op.target -Destination $snapshot
}
try {
    foreach ($op in $operations) {
        $source = if ($Action -eq 'Install') { $op.source } else { $op.backup }
        Copy-Item -LiteralPath $source -Destination $op.target -Force
        if ((Get-PackageHash -LiteralPath $op.target).Hash -ne (Get-PackageHash -LiteralPath $source).Hash) { throw 'Falha na verificacao da copia.' }
    }
} catch {
    foreach ($op in $operations) { Copy-Item -LiteralPath (Inside $transactionRoot $op.path) -Destination $op.target -Force }
    throw
}
Write-Output "$Action concluido: $($operations.Count) arquivos verificados; backup em $backupRoot."
