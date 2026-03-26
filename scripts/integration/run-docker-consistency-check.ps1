$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$tmpDir = Join-Path $root ".codex-tmp"
$logFile = Join-Path $tmpDir "docker-consistency.log"

New-Item -ItemType Directory -Force $tmpDir | Out-Null

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker is not available in PATH. Skipping Docker/PostgreSQL/Redis consistency check."
    exit 2
}

Write-Host "Starting postgres and redis via Docker Compose..."
docker compose up -d postgres redis | Tee-Object -FilePath $logFile

Write-Host "Running lightweight backend tests for SQLite baseline..."
powershell -ExecutionPolicy Bypass -File "$root\scripts\local\run-backend-tests.ps1"

Write-Host "Docker services started. Next step is to run API against PostgreSQL/Redis and compare behavior."
Write-Host "This script currently verifies environment readiness and baseline test execution."
