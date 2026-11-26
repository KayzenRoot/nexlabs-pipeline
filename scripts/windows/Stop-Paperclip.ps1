[CmdletBinding()]
param(
    [string]$Root
)

. (Join-Path $PSScriptRoot 'Paperclip.Common.ps1')

try {
    Assert-PaperclipDocker
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 2
}

try {
    $repositoryRoot = Get-PaperclipRepositoryRoot
    $paths = Get-PaperclipPaths -Root $Root
    if (-not (Test-Path $paths.SecretFile)) {
        Write-Error 'SECRETS_FILE_MISSING: cannot resolve compose environment'
        exit 3
    }
    $secrets = Read-PaperclipEnvFile -Path $paths.SecretFile
    Assert-PaperclipSecrets -Values $secrets
    Set-PaperclipLocalEnvironment -RepositoryRoot $repositoryRoot -DataDir $paths.Data

    # Graceful stop only. Never remove volumes or use a destructive compose teardown.
    Invoke-PaperclipCompose -RepositoryRoot $repositoryRoot -SecretFile $paths.SecretFile -ComposeCommand @('stop')
    Write-Output 'PAPERCLIP_STOPPED_DATA_PRESERVED'
    exit 0
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
