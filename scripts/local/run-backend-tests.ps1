$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$venvPip = Join-Path $root ".venv\Scripts\pip.exe"
$localDataDir = Join-Path $root ".local"
$sqlitePath = Join-Path $localDataDir "marp-test.db"

New-Item -ItemType Directory -Force $localDataDir | Out-Null

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating Python 3.12 virtual environment..."
    & py -3.12 -m venv "$root\.venv"
}

Write-Host "Installing backend dependencies if needed..."
& $venvPython -c "import fastapi, pydantic, sqlalchemy, pytest" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $venvPip install --disable-pip-version-check --upgrade pip setuptools wheel | Out-Host
    & $venvPip install "$root\services\api[dev]" | Out-Host
}

$env:MARP_ENV = "test-local"
$env:MARP_DATABASE_URL = "sqlite+aiosqlite:///$($sqlitePath -replace '\\','/')"
$env:MARP_REDIS_URL = "redis://localhost:6379/0"
$env:MARP_DB_AUTO_CREATE_SCHEMA = "true"

& $venvPython -m pytest "$root\services\api\tests"
