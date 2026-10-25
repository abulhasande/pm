$ErrorActionPreference = "Stop"
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}

docker compose up --build -d
Write-Host "PM app is starting on http://localhost:8000"
