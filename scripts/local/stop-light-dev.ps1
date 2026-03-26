$ErrorActionPreference = "SilentlyContinue"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$tmpDir = Join-Path $root ".codex-tmp"
$pidFiles = @(
    (Join-Path $tmpDir "api.pid"),
    (Join-Path $tmpDir "web.pid")
)

foreach ($pidFile in $pidFiles) {
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        if ($pid) {
            Stop-Process -Id ([int]$pid) -Force
        }
        Remove-Item $pidFile -Force
    }
}

Write-Host "Local services stopped."

