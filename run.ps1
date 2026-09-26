# NER-LogiX Startup Script (PowerShell)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host " NER-LogiX: North Eastern Logistics Intelligence Platform" -ForegroundColor Green
Write-Host " AI-Powered Accessibility & Disruption Management" -ForegroundColor Yellow
Write-Host "===========================================================" -ForegroundColor Cyan

$PythonExe = "$ScriptDir\python_env\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python.exe"
}

Write-Host "Launching NER-LogiX Server on http://localhost:8080 ..." -ForegroundColor White
Start-Process "http://localhost:8080"

& $PythonExe "$ScriptDir\server.py" 8080
