# Shared helpers for the local-first Paperclip deployment.
# Compatible with Windows PowerShell 5.1+. Never prints secret values.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-PaperclipRepositoryRoot {
    param([string]$StartPath = $PSScriptRoot)
    $candidate = [IO.Path]::GetFullPath((Join-Path $StartPath '..\..'))
    if (-not (Test-Path (Join-Path $candidate 'deploy\compose.yaml'))) {
        throw "PAPERCLIP_REPOSITORY_ROOT_NOT_FOUND: expected deploy/compose.yaml under $candidate"
    }
    return $candidate
}

function Get-PaperclipRoot {
    param([string]$Root)
    if ($Root) { return [IO.Path]::GetFullPath($Root) }
    if ($env:NEXLABS_PAPERCLIP_ROOT) { return [IO.Path]::GetFullPath($env:NEXLABS_PAPERCLIP_ROOT) }
    if (Test-Path 'D:\') { return 'D:\NexLabs\Paperclip' }
    return (Join-Path $env:LOCALAPPDATA 'NexLabs\Paperclip')
}

function Get-PaperclipPaths {
    param([string]$Root)
    $rootPath = Get-PaperclipRoot -Root $Root
    return [ordered]@{
        Root       = $rootPath
        Data       = (Join-Path $rootPath 'data')
        Secrets    = (Join-Path $rootPath 'secrets')
        SecretFile = (Join-Path (Join-Path $rootPath 'secrets') 'paperclip.env')
        Backups    = (Join-Path $rootPath 'backups')
    }
}

function New-PaperclipDirectory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Set-OwnerOnlyAcl {
    param([string]$Path)
    if ($env:OS -ne 'Windows_NT') { return }
    if (-not (Test-Path $Path)) { throw "ACL_TARGET_MISSING: $Path" }
    $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $item = Get-Item -LiteralPath $Path -Force
    $grant = if ($item.PSIsContainer) { "${user}:(OI)(CI)F" } else { "${user}:F" }
    & icacls $Path /reset 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "ACL_RESET_FAILED: $Path" }
    & icacls $Path /inheritance:r 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "ACL_INHERITANCE_REMOVE_FAILED: $Path" }
    & icacls $Path /grant:r $grant 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "ACL_APPLICATION_FAILED: $Path" }
}

function New-PaperclipSecretHex {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    return [BitConverter]::ToString($bytes).Replace('-', '').ToLowerInvariant()
}

function Read-PaperclipEnvFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { throw "SECRETS_FILE_MISSING: $Path" }
    $values = @{}
    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith('#')) { continue }
        $index = $trimmed.IndexOf('=')
        if ($index -lt 1) { continue }
        $key = $trimmed.Substring(0, $index).Trim()
        $value = $trimmed.Substring($index + 1).Trim()
        $values[$key] = $value
    }
    return $values
}

function Assert-PaperclipSecrets {
    param([hashtable]$Values)
    foreach ($name in @('BETTER_AUTH_SECRET', 'PAPERCLIP_TOOL_ACTION_SIGNING_SECRET')) {
        if (-not $Values.ContainsKey($name)) { throw "SECRET_MISSING: $name" }
        $value = [string]$Values[$name]
        if ($value -notmatch '^[0-9a-fA-F]{64}$') { throw "SECRET_INVALID: $name must be 64 hex characters" }
    }
}

function Write-PaperclipSecrets {
    param(
        [string]$SecretFile,
        [switch]$Rotate
    )
    if (Test-Path $SecretFile) {
        $existing = Read-PaperclipEnvFile -Path $SecretFile
        Assert-PaperclipSecrets -Values $existing
        if (-not $Rotate) { return $false }
    }
    New-PaperclipDirectory -Path (Split-Path -Parent $SecretFile)
    Set-OwnerOnlyAcl -Path (Split-Path -Parent $SecretFile)
    $auth = New-PaperclipSecretHex
    $tool = New-PaperclipSecretHex
    $content = "BETTER_AUTH_SECRET=$auth`nPAPERCLIP_TOOL_ACTION_SIGNING_SECRET=$tool`n"
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($SecretFile, $content, $utf8)
    Set-OwnerOnlyAcl -Path $SecretFile
    return $true
}

function Enable-PaperclipDockerCli {
    if (Get-Command docker -ErrorAction SilentlyContinue) { return $true }
    $candidates = @(
        (Join-Path $env:ProgramFiles 'Docker\Docker\resources\bin')
    )
    foreach ($candidate in $candidates) {
        $exe = Join-Path $candidate 'docker.exe'
        if (Test-Path $exe) {
            $env:Path = "$candidate;$env:Path"
            return $true
        }
    }
    return $false
}

function Test-PaperclipDocker {
    if (-not (Enable-PaperclipDockerCli)) { return $false }
    try {
        & docker version --format '{{.Server.Version}}' 2>$null | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Assert-PaperclipDocker {
    if (-not (Enable-PaperclipDockerCli)) {
        throw 'DOCKER_CLI_MISSING: install Docker Desktop with WSL2 backend; this WO will not install it without owner authorization'
    }
    & docker version --format '{{.Server.Version}}' 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'DOCKER_DAEMON_UNAVAILABLE: start Docker Desktop with WSL2 backend; this WO will not start/enable it without owner authorization'
    }
}

function Get-PaperclipImageReference {
    param([string]$RepositoryRoot)
    $lockPath = Join-Path $RepositoryRoot 'deploy\image-lock.json'
    $lock = Get-Content -LiteralPath $lockPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (-not $lock.paperclip.image) { throw 'IMAGE_LOCK_PAPERCLIP_MISSING' }
    return [string]$lock.paperclip.image
}

function Set-PaperclipLocalEnvironment {
    param(
        [string]$RepositoryRoot,
        [string]$DataDir,
        [int]$Port = 3100
    )
    $env:PAPERCLIP_IMAGE = Get-PaperclipImageReference -RepositoryRoot $RepositoryRoot
    $env:PAPERCLIP_DATA_DIR = $DataDir.Replace('\', '/')
    $env:PAPERCLIP_PORT = [string]$Port
    $env:PAPERCLIP_PUBLIC_URL = "http://localhost:$Port"
}

function Get-PaperclipComposeArguments {
    param(
        [string]$RepositoryRoot,
        [string]$SecretFile,
        [string[]]$ComposeCommand
    )
    $commandArgs = @(
        'compose',
        '-p', 'nexlabs-paperclip',
        '--env-file', $SecretFile,
        '-f', (Join-Path $RepositoryRoot 'deploy\compose.yaml'),
        '-f', (Join-Path $RepositoryRoot 'deploy\local\compose.yaml')
    )
    if ($ComposeCommand) { $commandArgs += $ComposeCommand }
    return $commandArgs
}

function Invoke-PaperclipCompose {
    param(
        [string]$RepositoryRoot,
        [string]$SecretFile,
        [string[]]$ComposeCommand,
        [switch]$Quiet
    )
    $arguments = Get-PaperclipComposeArguments -RepositoryRoot $RepositoryRoot -SecretFile $SecretFile -ComposeCommand $ComposeCommand
    $previousProjectName = $env:COMPOSE_PROJECT_NAME
    $env:COMPOSE_PROJECT_NAME = 'nexlabs-paperclip'
    try {
        if ($Quiet) {
            & docker @arguments 2>&1 | Out-Null
        } else {
            & docker @arguments
        }
        $exitCode = $LASTEXITCODE
    } finally {
        if ($null -eq $previousProjectName) {
            Remove-Item Env:COMPOSE_PROJECT_NAME -ErrorAction SilentlyContinue
        } else {
            $env:COMPOSE_PROJECT_NAME = $previousProjectName
        }
    }
    if ($exitCode -ne 0) { throw "COMPOSE_COMMAND_FAILED: $($ComposeCommand -join ' ')" }
}

function Get-PaperclipPortState {
    param([int]$Port = 3100)
    $listeners = @()
    if (Get-Command Get-NetTCPConnection -ErrorAction SilentlyContinue) {
        $listeners = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    } else {
        $lines = & netstat -ano 2>$null | Select-String -Pattern "LISTENING\s+\d+$"
        foreach ($line in $lines) {
            $parts = ($line.ToString() -split '\s+') | Where-Object { $_ }
            if ($parts.Count -ge 5 -and $parts[1] -match ":$Port$") {
                $listeners += [pscustomobject]@{ LocalAddress = $parts[1]; OwningProcess = [int]$parts[-1] }
            }
        }
    }
    return [pscustomobject]@{
        InUse          = ($listeners.Count -gt 0)
        ListenerCount  = $listeners.Count
        OwningProcess  = $(if ($listeners.Count -gt 0) { $listeners[0].OwningProcess } else { $null })
    }
}

function Get-PaperclipHealth {
    param([int]$Port = 3100)
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$Port/api/health" -TimeoutSec 5
        return [pscustomobject]@{ Ok = ($response.StatusCode -eq 200); StatusCode = $response.StatusCode }
    } catch {
        return [pscustomobject]@{ Ok = $false; StatusCode = 0 }
    }
}

function Wait-PaperclipHealth {
    param([int]$Port = 3100, [int]$TimeoutSeconds = 120)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $health = Get-PaperclipHealth -Port $Port
        if ($health.Ok) { return $true }
        Start-Sleep -Seconds 3
    }
    return $false
}

function New-PaperclipBackupArchive {
    param(
        [string]$DataDir,
        [string]$BackupDir
    )
    if (-not (Test-Path $DataDir)) { throw "DATA_DIR_MISSING: $DataDir" }
    $items = @(Get-ChildItem -LiteralPath $DataDir -Force)
    if ($items.Count -eq 0) { throw "DATA_DIR_EMPTY: $DataDir" }
    New-PaperclipDirectory -Path $BackupDir
    Set-OwnerOnlyAcl -Path $BackupDir
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $archive = Join-Path $BackupDir "paperclip-data-$stamp.zip"
    Get-ChildItem -LiteralPath $DataDir -Force | Compress-Archive -DestinationPath $archive -CompressionLevel Optimal
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
    $sidecar = "$archive.sha256"
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($sidecar, "$hash  $([IO.Path]::GetFileName($archive))`n", $utf8)
    Set-OwnerOnlyAcl -Path $archive
    Set-OwnerOnlyAcl -Path $sidecar
    return [pscustomobject]@{
        ArchivePath = $archive
        HashPath    = $sidecar
        Sha256      = $hash
    }
}

function Expand-PaperclipBackupArchive {
    param(
        [string]$ArchivePath,
        [string]$TargetDir,
        [switch]$Force
    )
    if (-not (Test-Path $ArchivePath)) { throw "BACKUP_MISSING: $ArchivePath" }
    $sidecar = "$ArchivePath.sha256"
    if (-not (Test-Path $sidecar)) { throw "BACKUP_SIDECAR_MISSING: $ArchivePath" }
    $expected = (Get-Content -LiteralPath $sidecar -TotalCount 1).Split(' ')[0].Trim().ToLowerInvariant()
    if ($expected -notmatch '^[0-9a-f]{64}$') { throw "BACKUP_SIDECAR_INVALID: $ArchivePath" }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $ArchivePath).Hash.ToLowerInvariant()
    if ($expected -ne $actual) { throw "BACKUP_HASH_MISMATCH: $ArchivePath" }
    if ((Test-Path $TargetDir) -and @(Get-ChildItem -LiteralPath $TargetDir -Force).Count -gt 0 -and -not $Force) {
        throw "RESTORE_TARGET_NOT_EMPTY: $TargetDir"
    }
    New-PaperclipDirectory -Path $TargetDir
    Expand-Archive -LiteralPath $ArchivePath -DestinationPath $TargetDir -Force:$Force
    return $TargetDir
}

function Repair-PaperclipRestoredPermissions {
    param([string]$DataDir)
    if (-not (Enable-PaperclipDockerCli)) { return $false }
    $dbDir = Join-Path $DataDir 'instances\default\db'
    if (-not (Test-Path $dbDir)) { return $false }
    $repositoryRoot = Get-PaperclipRepositoryRoot
    $image = Get-PaperclipImageReference -RepositoryRoot $repositoryRoot
    & docker image inspect $image 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { return $false }
    $mount = $DataDir.Replace('\', '/')
    & docker run --rm --entrypoint sh -v "${mount}:/paperclip" $image -c "chown -R node:node /paperclip/instances/default 2>/dev/null || true; chmod 700 /paperclip/instances/default; chmod -R go-rwx /paperclip/instances/default/db" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'RESTORE_PERMISSION_REPAIR_FAILED' }
    return $true
}
