[CmdletBinding()]
param(
    [string]$Root,
    [int]$Port = 3100
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
    New-PaperclipDirectory -Path $paths.Data
    Set-OwnerOnlyAcl -Path $paths.Data
    if (-not (Test-Path $paths.SecretFile)) {
        Write-Error "SECRETS_FILE_MISSING: run Initialize-PaperclipSecrets.ps1 first"
        exit 3
    }
    $secrets = Read-PaperclipEnvFile -Path $paths.SecretFile
    Assert-PaperclipSecrets -Values $secrets
    Set-PaperclipLocalEnvironment -RepositoryRoot $repositoryRoot -DataDir $paths.Data -Port $Port

    $portState = Get-PaperclipPortState -Port $Port
    if ($portState.InUse) {
        $health = Get-PaperclipHealth -Port $Port
        if (-not $health.Ok) {
            Write-Error "PORT_IN_USE: TCP $Port is occupied by a process that is not healthy Paperclip"
            exit 4
        }
        Write-Output "PAPERCLIP_ALREADY_READY http://localhost:$Port"
        exit 0
    }

    Invoke-PaperclipCompose -RepositoryRoot $repositoryRoot -SecretFile $paths.SecretFile -ComposeCommand @('up', '-d')
    if (-not (Wait-PaperclipHealth -Port $Port -TimeoutSeconds 420)) {
        Write-Error "PAPERCLIP_HEALTH_TIMEOUT: inspect docker compose ps and container logs"
        exit 5
    }
    Write-Output "PAPERCLIP_READY http://localhost:$Port"
    exit 0
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
