[CmdletBinding()]
param(
    [switch]$IncludeDocker
)

. (Join-Path $PSScriptRoot 'Paperclip.Common.ps1')

$script:PassCount = 0
$script:FailCount = 0

function Check-PaperclipTest {
    param([string]$Name, [bool]$Condition)
    if ($Condition) {
        $script:PassCount++
        Write-Output "PASS $Name"
    } else {
        $script:FailCount++
        Write-Output "FAIL $Name"
    }
}

function Write-PaperclipInfo {
    param([string]$Message)
    Write-Output "INFO $Message"
}

$repositoryRoot = Get-PaperclipRepositoryRoot
$tempRoot = Join-Path $env:TEMP ("paperclip-selftest-" + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $tempRoot -Force

try {
    $imageLockPath = Join-Path $repositoryRoot 'deploy\image-lock.json'
    $imageLock = Get-Content -LiteralPath $imageLockPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $paperclipImage = [string]$imageLock.paperclip.image
    $postgresImage = [string]$imageLock.postgres.image

    Check-PaperclipTest 'image_lock_paperclip_index_digest' ([bool]($imageLock.paperclip.index_digest -match '^sha256:[0-9a-f]{64}$'))
    Check-PaperclipTest 'image_lock_postgres_index_digest' ([bool]($imageLock.postgres.index_digest -match '^sha256:[0-9a-f]{64}$'))
    Check-PaperclipTest 'image_lock_amd64' ([bool]($imageLock.paperclip.platforms.'linux/amd64'.digest -match '^sha256:'))
    Check-PaperclipTest 'image_lock_arm64' ([bool]($imageLock.paperclip.platforms.'linux/arm64'.digest -match '^sha256:'))
    Check-PaperclipTest 'image_lock_pinned_reference' ([bool]($paperclipImage -match ':2026\.1117\.0@sha256:[0-9a-f]{64}$'))

    $baseCompose = Get-Content -LiteralPath (Join-Path $repositoryRoot 'deploy\compose.yaml') -Raw -Encoding UTF8
    $localCompose = Get-Content -LiteralPath (Join-Path $repositoryRoot 'deploy\local\compose.yaml') -Raw -Encoding UTF8
    $vpsCompose = Get-Content -LiteralPath (Join-Path $repositoryRoot 'deploy\vps\compose.yaml') -Raw -Encoding UTF8

    Check-PaperclipTest 'compose_uses_image_lock' ($baseCompose.Contains($paperclipImage))
    Check-PaperclipTest 'compose_healthcheck_api' ($baseCompose -match '/api/health')
    Check-PaperclipTest 'compose_requires_auth_secret' ($baseCompose -match 'BETTER_AUTH_SECRET')
    Check-PaperclipTest 'compose_requires_tool_secret' ($baseCompose -match 'PAPERCLIP_TOOL_ACTION_SIGNING_SECRET')
    Check-PaperclipTest 'local_loopback_bind' ([bool]($localCompose -match '127\.0\.0\.1:' -and $localCompose -notmatch '0\.0\.0\.0'))
    Check-PaperclipTest 'local_persistent_volume' ([bool]($localCompose -match '/paperclip'))
    Check-PaperclipTest 'no_latest_tag' (-not (($baseCompose + $localCompose + $vpsCompose) -match ':latest'))
    Check-PaperclipTest 'vps_postgres_pinned' ($vpsCompose.Contains($postgresImage))
    Check-PaperclipTest 'vps_database_url_required' ($vpsCompose -match 'DATABASE_URL')
    Check-PaperclipTest 'vps_no_public_bind' ([bool]($vpsCompose -match '127\.0\.0\.1:' -and $vpsCompose -notmatch '0\.0\.0\.0'))

    $scriptText = ''
    foreach ($scriptFile in Get-ChildItem -LiteralPath (Join-Path $repositoryRoot 'scripts\windows') -Filter '*.ps1' | Where-Object { $_.Name -ne 'Test-PaperclipDeployment.ps1' }) {
        $scriptText += (Get-Content -LiteralPath $scriptFile.FullName -Raw -Encoding UTF8)
    }
    Check-PaperclipTest 'no_down_v' (-not ($scriptText -match 'down\s+-v'))
    Check-PaperclipTest 'no_docker_system_prune' (-not ($scriptText -match 'system\s+prune'))
    Check-PaperclipTest 'no_force_recreate' (-not ($scriptText -match '--force-recreate'))

    $tempData = Join-Path $tempRoot 'data'
    $tempSecrets = Join-Path $tempRoot 'secrets'
    $tempBackups = Join-Path $tempRoot 'backups'
    $tempRestore = Join-Path $tempRoot 'restore'
    $tempSecretFile = Join-Path $tempSecrets 'paperclip.env'
    New-PaperclipDirectory -Path $tempData
    New-PaperclipDirectory -Path $tempSecrets
    Set-OwnerOnlyAcl -Path $tempSecrets

    $created = Write-PaperclipSecrets -SecretFile $tempSecretFile
    $values = Read-PaperclipEnvFile -Path $tempSecretFile
    Assert-PaperclipSecrets -Values $values
    $secretFileCreated = [bool]($created -and (Test-Path $tempSecretFile))
    $secretLengthsValid = [bool]($values['BETTER_AUTH_SECRET'].Length -eq 64 -and $values['PAPERCLIP_TOOL_ACTION_SIGNING_SECRET'].Length -eq 64)
    $secretValuesIndependent = [bool]($values['BETTER_AUTH_SECRET'] -ne $values['PAPERCLIP_TOOL_ACTION_SIGNING_SECRET'])
    Check-PaperclipTest 'secret_file_created' $secretFileCreated
    Check-PaperclipTest 'secret_lengths_valid' $secretLengthsValid
    Check-PaperclipTest 'secret_values_independent' $secretValuesIndependent
    if ($env:OS -eq 'Windows_NT') {
        $acl = Get-Acl -LiteralPath $tempSecrets
        Check-PaperclipTest 'secret_directory_acl_protected' ([bool]$acl.AreAccessRulesProtected)
    }

    [IO.File]::WriteAllText((Join-Path $tempData 'sentinel-a.txt'), 'A', (New-Object System.Text.UTF8Encoding($false)))
    $nested = Join-Path $tempData 'nested'
    New-PaperclipDirectory -Path $nested
    [IO.File]::WriteAllText((Join-Path $nested 'sentinel-b.txt'), 'B', (New-Object System.Text.UTF8Encoding($false)))

    $backup = New-PaperclipBackupArchive -DataDir $tempData -BackupDir $tempBackups
    Check-PaperclipTest 'backup_archive_created' ([bool](Test-Path $backup.ArchivePath))
    Check-PaperclipTest 'backup_hash_sidecar' ([bool](Test-Path $backup.HashPath))
    Check-PaperclipTest 'backup_hash_64_hex' ([bool]($backup.Sha256 -match '^[0-9a-f]{64}$'))

    $null = Expand-PaperclipBackupArchive -ArchivePath $backup.ArchivePath -TargetDir $tempRestore
    $restoredA = Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $tempRestore 'sentinel-a.txt')
    $restoredB = Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $tempRestore 'nested\sentinel-b.txt')
    $expectedA = Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $tempData 'sentinel-a.txt')
    $expectedB = Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $tempData 'nested\sentinel-b.txt')
    Check-PaperclipTest 'restore_sentinel_a' ([bool]($restoredA.Hash -eq $expectedA.Hash))
    Check-PaperclipTest 'restore_sentinel_b' ([bool]($restoredB.Hash -eq $expectedB.Hash))

    $tampered = Join-Path $tempRoot 'tampered.zip'
    [IO.File]::Copy($backup.ArchivePath, $tampered, $true)
    $tamperedBytes = [IO.File]::ReadAllBytes($tampered)
    [IO.File]::WriteAllBytes($tampered, ($tamperedBytes + [byte]0))
    [IO.File]::Copy($backup.HashPath, "$tampered.sha256", $true)
    $tamperDetected = $false
    try {
        $null = Expand-PaperclipBackupArchive -ArchivePath $tampered -TargetDir (Join-Path $tempRoot 'tampered-restore')
    } catch {
        $tamperDetected = $true
    }
    Check-PaperclipTest 'tamper_detection' ([bool]$tamperDetected)

    $noSidecar = Join-Path $tempRoot 'no-sidecar.zip'
    [IO.File]::Copy($backup.ArchivePath, $noSidecar, $true)
    $sidecarRequired = $false
    try {
        $null = Expand-PaperclipBackupArchive -ArchivePath $noSidecar -TargetDir (Join-Path $tempRoot 'no-sidecar-restore')
    } catch {
        $sidecarRequired = $true
    }
    Check-PaperclipTest 'restore_requires_sidecar' ([bool]$sidecarRequired)

    $portState = Get-PaperclipPortState -Port 3100
    if ($portState.InUse) {
        $health = Get-PaperclipHealth -Port 3100
        Check-PaperclipTest 'port_3100_available_or_healthy' ([bool]$health.Ok)
    } else {
        Check-PaperclipTest 'port_3100_available_or_healthy' $true
    }

    $dockerAvailable = Test-PaperclipDocker
    Write-PaperclipInfo ("DOCKER_AVAILABLE=" + $dockerAvailable)
    if ($IncludeDocker) {
        if ($dockerAvailable) {
            Set-PaperclipLocalEnvironment -RepositoryRoot $repositoryRoot -DataDir $tempData -Port 3101
            Invoke-PaperclipCompose -RepositoryRoot $repositoryRoot -SecretFile $tempSecretFile -ComposeCommand @('config', '--quiet') -Quiet
            Check-PaperclipTest 'docker_compose_config' $true
        } else {
            Write-PaperclipInfo 'DOCKER_COMPOSE_CONFIG_SKIPPED_DOCKER_ABSENT'
        }
    }
} catch {
    Check-PaperclipTest 'unexpected_error' $false
    Write-Output "ERROR $($_.Exception.Message)"
    Write-Output "ERROR_AT $($_.InvocationInfo.PositionMessage)"
    Write-Output "ERROR_STACK $($_.ScriptStackTrace)"
} finally {
    if (Test-Path $tempRoot) {
        [IO.Directory]::Delete($tempRoot, $true)
    }
}

Write-Output "SELFTEST_PASS=$($script:PassCount) SELFTEST_FAIL=$($script:FailCount)"
if ($script:FailCount -gt 0) { exit 1 }
exit 0
