$ErrorActionPreference = "Stop"
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

docker compose down --remove-orphans
Write-Host "PM app stopped"
