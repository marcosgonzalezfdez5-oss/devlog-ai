<#
Starts the Task Manager backend (FastAPI/uvicorn) and frontend (Streamlit),
each in its own window. Creates each venv and installs dependencies on first run.
#>

$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"

function Initialize-App {
    param([string]$Dir)

    $venvPath = Join-Path $Dir "venv"
    $pythonExe = Join-Path $venvPath "Scripts\python.exe"

    if (-not (Test-Path $pythonExe)) {
        Write-Host "Creating venv in $Dir ..."
        py -3.13 -m venv $venvPath
        & $pythonExe -m pip install -q --upgrade pip
        & $pythonExe -m pip install -q -r (Join-Path $Dir "requirements.txt")
    }

    $envFile = Join-Path $Dir ".env"
    $envExample = Join-Path $Dir ".env.example"
    if ((-not (Test-Path $envFile)) -and (Test-Path $envExample)) {
        Copy-Item $envExample $envFile
        Write-Warning "Created $envFile from .env.example - fill in real values before using the app."
    }
}

Initialize-App -Dir $backendDir
Initialize-App -Dir $frontendDir

$backendPython = Join-Path $backendDir "venv\Scripts\python.exe"
$frontendPython = Join-Path $frontendDir "venv\Scripts\python.exe"

Write-Host "Starting backend (FastAPI) on http://localhost:8000 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$backendDir'; & '$backendPython' -m uvicorn app.main:app --reload --port 8000"
)

Start-Sleep -Seconds 2

Write-Host "Starting frontend (Streamlit) on http://localhost:8501 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$frontendDir'; & '$frontendPython' -m streamlit run app.py"
)

Write-Host "Both apps are starting in separate windows. Close those windows to stop them."
