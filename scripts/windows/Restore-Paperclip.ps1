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
    if ($Force) { throw 'RESTORE_FORCE_FORBIDDEN' }
    $paths = Get-PaperclipPaths -Root $Root
    $archive = [IO.Path]::GetFullPath($BackupPath)
    if (-not $TargetDataDir) {
        $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
        $suffix = [guid]::NewGuid().ToString("N")
        $TargetDataDir = Join-Path $paths.Root "restore-test-$stamp-$suffix"
    }
    $target = [IO.Path]::GetFullPath($TargetDataDir)
    Assert-PaperclipIsolatedRestoreTarget -Root $paths.Root -TargetDir $target
    Expand-PaperclipBackupArchive -ArchivePath $archive -TargetDir $target
    $entries = @(Get-ChildItem -LiteralPath $target -Force)
    if ($entries.Count -eq 0) { throw 'RESTORE_EMPTY_TARGET' }
    $repaired = Repair-PaperclipRestoredPermissions -DataDir $target
    if ($repaired) {
        Write-Output 'RESTORE_PERMISSIONS_REPAIRED'
    } else {
        Write-Output 'RESTORE_PERMISSIONS_NOT_REPAIRED_DOCKER_OR_IMAGE_UNAVAILABLE'
    }
    Write-Output "RESTORE_OK target=$target entries=$($entries.Count)"
    Write-Output 'LIVE_DATA_NOT_REPLACED: validate the isolated restore before any manual swap'
    exit 0
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
