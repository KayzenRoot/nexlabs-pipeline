# NLE-INFRA-WO-001: strictly read-only Windows inventory.
# Compatible with Windows PowerShell 5.1+; no installation or configuration changes.
$ErrorActionPreference = "Continue"

function Invoke-SafeText {
    param([string]$Name, [string[]]$Arguments = @())
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { return "NOT_AVAILABLE" }
    try {
        $value = & $Name @Arguments 2>&1 | Out-String
        if ([string]::IsNullOrWhiteSpace($value)) { return "NO_OUTPUT" }
        return $value.Trim()
    } catch {
        return "ERROR"
    }
}

function Get-BindScope {
    param([string]$Address)
    if ($Address -in @("0.0.0.0", "::", "*")) { return "WILDCARD" }
    if ($Address -in @("127.0.0.1", "::1")) { return "LOOPBACK" }
    return "SPECIFIC_INTERFACE"
}

$os = $null
$computer = $null
$processors = @()
$gpus = @()
$volumes = @()
$services = @()
$listeners = @()

try { $os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber, OSArchitecture } catch { $os = "NOT_AVAILABLE" }
try {
    $computer = Get-CimInstance Win32_ComputerSystem
    $computer = [ordered]@{
        Manufacturer = $computer.Manufacturer
        Model = $computer.Model
        PhysicalMemoryGiB = [math]::Round(($computer.TotalPhysicalMemory / 1GB), 2)
    }
} catch { $computer = "NOT_AVAILABLE" }

try {
    $processors = @(Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors)
} catch { $processors = @("NOT_AVAILABLE") }
try {
    $gpus = @(Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, AdapterRAM)
} catch { $gpus = @("NOT_AVAILABLE") }
try {
    $volumes = @(Get-Volume | Where-Object { $_.DriveLetter } | ForEach-Object {
        [ordered]@{
            Drive = "$($_.DriveLetter):"
            FileSystem = $_.FileSystem
            SizeGiB = [math]::Round(($_.Size / 1GB), 2)
            FreeGiB = [math]::Round(($_.SizeRemaining / 1GB), 2)
        }
    })
} catch { $volumes = @("NOT_AVAILABLE") }
try {
    $services = @(Get-Service | Where-Object { $_.Name -match "docker|wireguard|ssh" } |
        Select-Object Name, Status, StartType)
} catch { $services = @("NOT_AVAILABLE") }
try {
    $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop |
        ForEach-Object {
            [ordered]@{
                BindScope = Get-BindScope -Address $_.LocalAddress
                Port = $_.LocalPort
            }
        } | Sort-Object BindScope, Port -Unique)
} catch { $listeners = @("NOT_AVAILABLE") }

$wslStatus = Invoke-SafeText -Name "wsl" -Arguments @("--status")
$wslDistributions = Invoke-SafeText -Name "wsl" -Arguments @("--list", "--verbose")
$dockerVersion = Invoke-SafeText -Name "docker" -Arguments @("version", "--format", "{{.Client.Version}}|{{.Server.Version}}")
$dockerCompose = Invoke-SafeText -Name "docker" -Arguments @("compose", "version", "--short")
$dockerPs = Invoke-SafeText -Name "docker" -Arguments @("ps", "--format", "{{.Names}}|{{.Image}}|{{.Status}}|{{.Ports}}")
$dockerStats = Invoke-SafeText -Name "docker" -Arguments @("stats", "--no-stream", "--format", "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}")

# Keep only a status classification; never persist raw Codex login output or account identifiers.
$codexLoginStatus = "UNKNOWN"
if (Get-Command codex -ErrorAction SilentlyContinue) {
    try {
        $loginOutput = (& codex login status 2>&1 | Out-String)
        if ($loginOutput -match "(?i)not logged in|not authenticated|unauthenticated") {
            $codexLoginStatus = "NOT_AUTHENTICATED"
        } elseif ($loginOutput -match "(?i)logged in|authenticated") {
            $codexLoginStatus = "AUTHENTICATED"
        }
    } catch { $codexLoginStatus = "UNKNOWN" }
}

$dockerPs = $dockerPs -replace '(?:\d{1,3}\.){3}\d{1,3}(?=:)', '[IPv4]' -replace '\[[0-9a-fA-F:]+\](?=:)', '[IPv6]'

$report = [ordered]@{
    schemaVersion = "1.0"
    workOrder = "NLE-INFRA-WO-001"
    collectedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
    scope = "READ_ONLY"
    operatingSystem = $os
    system = $computer
    processors = $processors
    graphics = $gpus
    volumes = $volumes
    wsl = [ordered]@{
        status = $wslStatus
        distributions = $wslDistributions
    }
    docker = [ordered]@{
        version = $dockerVersion
        composeVersion = $dockerCompose
        runningContainers = $dockerPs
        resourceUsage = $dockerStats
    }
    codex = [ordered]@{
        version = (Invoke-SafeText -Name "codex" -Arguments @("--version"))
        loginStatus = $codexLoginStatus
    }
    git = (Invoke-SafeText -Name "git" -Arguments @("--version"))
    ssh = (Invoke-SafeText -Name "ssh" -Arguments @("-V"))
    listeningTcp = $listeners
    relevantServices = $services
    safety = [ordered]@{
        environmentVariablesRead = $false
        secretFilesRead = $false
        processArgumentsRead = $false
        credentialsPersisted = $false
        networkProbesRun = $false
        configurationChanged = $false
        filesWritten = $false
    }
}

$report | ConvertTo-Json -Depth 7
