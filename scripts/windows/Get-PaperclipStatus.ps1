[CmdletBinding()]
param(
    [string]$Root,
    [int]$Port = 3100
)

. (Join-Path $PSScriptRoot 'Paperclip.Common.ps1')

if (-not (Test-PaperclipDocker)) {
    Write-Output 'DOCKER_UNAVAILABLE: Docker Desktop/WSL2 is not running'
    exit 2
}

try {
    $repositoryRoot = Get-PaperclipRepositoryRoot
    $paths = Get-PaperclipPaths -Root $Root
    if (-not (Test-Path $paths.SecretFile)) {
        Write-Output 'SECRETS_FILE_MISSING'
        exit 3
    }
    $secrets = Read-PaperclipEnvFile -Path $paths.SecretFile
    Assert-PaperclipSecrets -Values $secrets
    Set-PaperclipLocalEnvironment -RepositoryRoot $repositoryRoot -DataDir $paths.Data -Port $Port

    Invoke-PaperclipCompose -RepositoryRoot $repositoryRoot -SecretFile $paths.SecretFile -ComposeCommand @('ps')
    $health = Get-PaperclipHealth -Port $Port
    if ($health.Ok) {
        Write-Output "HEALTH_OK http://localhost:$Port/api/health"
        Write-Output "DATA_DIR=$($paths.Data)"
        exit 0
    }
    Write-Output 'HEALTH_FAIL'
    exit 6
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
