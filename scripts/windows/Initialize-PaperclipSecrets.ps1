[CmdletBinding()]
param(
    [string]$Root,
    [switch]$Rotate
)

. (Join-Path $PSScriptRoot 'Paperclip.Common.ps1')

try {
    $paths = Get-PaperclipPaths -Root $Root
    New-PaperclipDirectory -Path $paths.Root
    Set-OwnerOnlyAcl -Path $paths.Root
    New-PaperclipDirectory -Path $paths.Data
    New-PaperclipDirectory -Path $paths.Secrets
    New-PaperclipDirectory -Path $paths.Backups
    Set-OwnerOnlyAcl -Path $paths.Secrets
    Set-OwnerOnlyAcl -Path $paths.Backups

    $created = Write-PaperclipSecrets -SecretFile $paths.SecretFile -Rotate:$Rotate
    $values = Read-PaperclipEnvFile -Path $paths.SecretFile
    Assert-PaperclipSecrets -Values $values

    if ($created) {
        Write-Output 'PAPERCLIP_SECRETS_CREATED'
    } else {
        Write-Output 'PAPERCLIP_SECRETS_PRESENT'
    }
    Write-Output "SECRETS_FILE=$($paths.SecretFile)"
    Write-Output 'VALUES_NOT_PRINTED'
    exit 0
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
