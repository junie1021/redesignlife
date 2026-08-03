[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$frontendPath = Join-Path $projectRoot "frontend\frontend"
$nodeModulesPath = Join-Path $frontendPath "node_modules"
$envPath = Join-Path $projectRoot ".env"
$backendProcess = $null
$previousLocation = Get-Location

if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
    throw "Python virtual environment not found. Create .venv and install backend/requirements-dev.txt first."
}

if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    throw "npm.cmd was not found. Install Node.js and try again."
}

if (-not (Test-Path -LiteralPath $nodeModulesPath -PathType Container)) {
    throw "Frontend dependencies are missing. Run 'npm.cmd ci' in frontend/frontend first."
}

if (-not (Test-Path -LiteralPath $envPath -PathType Leaf)) {
    Write-Warning "Root .env was not found. The app will run, but AI requests require OPENAI_API_KEY."
}

try {
    Write-Host "Starting backend at http://127.0.0.1:8000 ..."
    $backendProcess = Start-Process `
        -FilePath $pythonPath `
        -ArgumentList @(
            "-m", "uvicorn", "backend.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ) `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden `
        -PassThru

    $backendReady = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        if ($backendProcess.HasExited) {
            throw "The backend stopped during startup (exit code $($backendProcess.ExitCode))."
        }

        try {
            $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 1
            if ($health.success) {
                $backendReady = $true
                break
            }
        }
        catch {
            Start-Sleep -Milliseconds 250
        }
    }

    if (-not $backendReady) {
        throw "The backend did not become ready at http://127.0.0.1:8000/health."
    }

    Write-Host "Backend is ready. Starting frontend at http://localhost:5173 ..."
    Write-Host "Press Ctrl+C to stop both servers."
    Set-Location -LiteralPath $frontendPath
    & npm.cmd run dev

    if ($LASTEXITCODE -ne 0) {
        throw "The frontend stopped with exit code $LASTEXITCODE."
    }
}
finally {
    Set-Location -LiteralPath $previousLocation

    if ($null -ne $backendProcess -and -not $backendProcess.HasExited) {
        Write-Host "Stopping backend ..."
        & taskkill.exe /PID $backendProcess.Id /T /F 2>$null | Out-Null
    }
}
