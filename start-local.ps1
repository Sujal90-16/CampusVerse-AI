$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root 'backend'
$Frontend = Join-Path $Root 'frontend'
$BackendPython = Join-Path $Backend '.venv\Scripts\python.exe'
$FrontendEnv = Join-Path $Frontend '.env'

Write-Host "`nCampusVerse + SHAAN AI local launcher" -ForegroundColor Cyan
Write-Host "Project: $Root"

if (-not (Test-Path (Join-Path $Backend 'app\main.py'))) {
    throw 'Could not find backend\app\main.py. Keep start-local.ps1 in the CampusVerse project root.'
}
if (-not (Test-Path (Join-Path $Frontend 'package.json'))) {
    throw 'Could not find frontend\package.json. Keep start-local.ps1 in the CampusVerse project root.'
}

if (-not (Test-Path $BackendPython)) {
    Write-Host 'Backend virtual environment not found. Creating it and installing backend requirements...' -ForegroundColor Yellow
    py -m venv (Join-Path $Backend '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Could not create Python virtual environment. Check that Python is installed.' }
    & $BackendPython -m pip install --upgrade pip
    & $BackendPython -m pip install -r (Join-Path $Backend 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
}

# Use same-origin /api requests; Vite proxies them to FastAPI on port 8000.
# This avoids browser-to-backend host/CORS mismatches during local development.
Set-Content -Path $FrontendEnv -Value '# VITE_API_URL intentionally unset; local API requests use the Vite proxy.' -Encoding ascii

$backendAlreadyUp = $false
try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2
    if ($health.status -eq 'ok') { $backendAlreadyUp = $true; Write-Host 'Backend already responds on port 8000.' -ForegroundColor Green }
} catch {}

if (-not $backendAlreadyUp) {
    Write-Host 'Starting backend in a separate PowerShell window...' -ForegroundColor Cyan
    $backendCommand = "Set-Location -LiteralPath '$Backend'; & '$BackendPython' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
    Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoExit','-ExecutionPolicy','Bypass','-Command',$backendCommand) | Out-Null
}

$frontendAlreadyUp = $false
try { Invoke-WebRequest -Uri 'http://localhost:5173' -TimeoutSec 2 -UseBasicParsing | Out-Null; $frontendAlreadyUp = $true } catch {}
if (-not $frontendAlreadyUp) {
    if (-not (Test-Path (Join-Path $Frontend 'node_modules\vite\bin\vite.js'))) {
        Write-Host 'Frontend packages are missing. Installing npm dependencies (first run only)...' -ForegroundColor Yellow
        Push-Location $Frontend
        try { npm install; if ($LASTEXITCODE -ne 0) { throw 'npm install failed. Check your internet connection and Node.js installation.' } }
        finally { Pop-Location }
    }
    Write-Host 'Starting frontend in a separate PowerShell window...' -ForegroundColor Cyan
    $frontendCommand = "Set-Location -LiteralPath '$Frontend'; npm run dev -- --host 127.0.0.1"
    Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoExit','-ExecutionPolicy','Bypass','-Command',$frontendCommand) | Out-Null
}

Write-Host 'Waiting for the API to respond...' -ForegroundColor Cyan
$apiReady = $false
for ($i = 0; $i -lt 25; $i++) {
    try {
        $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2
        if ($health.status -eq 'ok') { $apiReady = $true; break }
    } catch {}
    Start-Sleep -Seconds 1
}
if ($apiReady) { Write-Host 'API is healthy.' -ForegroundColor Green }
else { Write-Host 'API did not respond yet. Check the separate backend window for a Python error.' -ForegroundColor Red }

Write-Host 'Opening CampusVerse at http://localhost:5173 ...' -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process 'http://localhost:5173'
Write-Host "`nKeep the backend and frontend PowerShell windows open while using CampusVerse." -ForegroundColor Yellow
