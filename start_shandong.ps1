$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

$pythonExe = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "Starting shandong dashboard..."
try {
    & $pythonExe "scripts\start_dashboard.py"
    if ($LASTEXITCODE -ne 0) {
        throw "Dashboard startup failed with exit code $LASTEXITCODE."
    }
} catch {
    Write-Host ""
    Write-Host "Dashboard startup failed: $_"
    Write-Host "If PowerShell blocks this script, run:"
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    exit 1
}

