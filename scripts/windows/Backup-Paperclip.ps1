[CmdletBinding()]
param(
    [string]$Root,
    [string]$BackupDir,
    [switch]$SkipServiceStop
)

. (Join-Path $PSScriptRoot 'Paperclip.Common.ps1')

try {
    $repositoryRoot = Get-PaperclipRepositoryRoot
    $paths = Get-PaperclipPaths -Root $Root
    $targetBackupDir = if ($BackupDir) { [IO.Path]::GetFullPath($BackupDir) } else { $paths.Backups }
    $secretFile = $paths.SecretFile
    $serviceStopped = $false

    if (-not $SkipServiceStop) {
        Assert-PaperclipDocker
        if (-not (Test-Path $secretFile)) { throw 'SECRETS_FILE_MISSING: cannot stop the service safely' }
        $secrets = Read-PaperclipEnvFile -Path $secretFile
        Assert-PaperclipSecrets -Values $secrets
        Set-PaperclipLocalEnvironment -RepositoryRoot $repositoryRoot -DataDir $paths.Data
        Invoke-PaperclipCompose -RepositoryRoot $repositoryRoot -SecretFile $secretFile -ComposeCommand @('stop')
        $serviceStopped = $true
    }

    try {
        $backup = New-PaperclipBackupArchive -DataDir $paths.Data -BackupDir $targetBackupDir
    } finally {
        if ($serviceStopped) {
            Set-PaperclipLocalEnvironment -RepositoryRoot $repositoryRoot -DataDir $paths.Data
            Invoke-PaperclipCompose -RepositoryRoot $repositoryRoot -SecretFile $secretFile -ComposeCommand @('start')
        }
    }

    Write-Output "BACKUP_OK path=$($backup.ArchivePath) sha256=$($backup.Sha256)"
    if ($serviceStopped) { Write-Output 'PAPERCLIP_RESTARTED_AFTER_BACKUP' }
    exit 0
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
