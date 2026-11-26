[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,
    [string]$TargetDataDir,
    [string]$Root,
    [switch]$Force
)

. (Join-Path $PSScriptRoot 'Paperclip.Common.ps1')

try {
    $paths = Get-PaperclipPaths -Root $Root
    $archive = [IO.Path]::GetFullPath($BackupPath)
    if (-not $TargetDataDir) {
        $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
        $TargetDataDir = Join-Path $paths.Root "restore-test-$stamp"
    }
    $target = [IO.Path]::GetFullPath($TargetDataDir)
    Expand-PaperclipBackupArchive -ArchivePath $archive -TargetDir $target -Force:$Force
    $entries = @(Get-ChildItem -LiteralPath $target -Force)
    if ($entries.Count -eq 0) { throw 'RESTORE_EMPTY_TARGET' }
    Write-Output "RESTORE_OK target=$target entries=$($entries.Count)"
    Write-Output 'LIVE_DATA_NOT_REPLACED: validate the isolated restore before any manual swap'
    exit 0
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
