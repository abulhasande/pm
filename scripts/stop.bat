@echo off
setlocal
cd /d "%~dp0.."

docker compose down --remove-orphans

echo PM app stopped
