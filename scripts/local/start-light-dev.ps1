param(
    [switch]$WithWeb
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$tmpDir = Join-Path $root ".codex-tmp"
$venvDir = Join-Path $root ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"
$apiPidFile = Join-Path $tmpDir "api.pid"
$webPidFile = Join-Path $tmpDir "web.pid"
$apiOut = Join-Path $tmpDir "api-light.out.log"
$apiErr = Join-Path $tmpDir "api-light.err.log"
$webOut = Join-Path $tmpDir "web-light.out.log"
$webErr = Join-Path $tmpDir "web-light.err.log"
$localDataDir = Join-Path $root ".local"
$sqlitePath = Join-Path $localDataDir "marp-dev.db"

New-Item -ItemType Directory -Force $tmpDir | Out-Null
New-Item -ItemType Directory -Force $localDataDir | Out-Null

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating Python 3.12 virtual environment..."
    & py -3.12 -m venv $venvDir
}

Write-Host "Installing backend dependencies if needed..."
& $venvPython -c "import fastapi, pydantic, sqlalchemy, uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $venvPip install --disable-pip-version-check --upgrade pip setuptools wheel | Out-Host
    & $venvPip install "$root\services\api[dev]" | Out-Host
}

$env:MARP_ENV = "local-light"
$env:MARP_DATABASE_URL = "sqlite+aiosqlite:///$($sqlitePath -replace '\\','/')"
$env:MARP_REDIS_URL = "redis://localhost:6379/0"
$env:MARP_DB_AUTO_CREATE_SCHEMA = "true"

Write-Host "Starting local API with SQLite..."
if (Test-Path $apiPidFile) {
    Remove-Item $apiPidFile -Force
}
$apiProcess = Start-Process `
    -FilePath $venvPython `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--app-dir", "$root\services\api", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $root `
    -RedirectStandardOutput $apiOut `
    -RedirectStandardError $apiErr `
    -PassThru
$apiProcess.Id | Set-Content $apiPidFile
Write-Host "API started at http://127.0.0.1:8000"

if ($WithWeb) {
    Write-Host "Starting local web frontend..."
    if (Test-Path $webPidFile) {
        Remove-Item $webPidFile -Force
    }
    $webProcess = Start-Process `
        -FilePath "npm.cmd" `
        -ArgumentList "run", "dev:web" `
        -WorkingDirectory $root `
        -RedirectStandardOutput $webOut `
        -RedirectStandardError $webErr `
        -PassThru
    $webProcess.Id | Set-Content $webPidFile
    Write-Host "Web started at http://127.0.0.1:3000"
}

Write-Host "Use scripts/local/stop-light-dev.ps1 to stop local services."
