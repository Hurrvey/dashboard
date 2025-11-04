Param(
    [string]$ProjectRoot
)

if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

Set-Location -Path $ProjectRoot

$ErrorActionPreference = 'Stop'
$env:PYTHONUNBUFFERED = '1'

$logPath = Join-Path -Path $ProjectRoot -ChildPath 'logs\backend.log'
if (-not (Test-Path -Path $logPath)) {
    New-Item -ItemType File -Path $logPath -Force | Out-Null
}

$pythonExe = Join-Path -Path $ProjectRoot -ChildPath 'venv\Scripts\python.exe'
if (-not (Test-Path -Path $pythonExe)) {
    Write-Error "Python executable not found: $pythonExe"
    exit 1
}

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$exitCode = 0

try {
    & $pythonExe 'run.py' 2>&1 | Tee-Object -FilePath $logPath -Append
    $exitCode = $LASTEXITCODE
}
finally {
    $ErrorActionPreference = $previousErrorActionPreference
}

if ($exitCode -ne 0) {
    exit $exitCode
}

