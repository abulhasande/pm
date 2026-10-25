@echo off
setlocal
cd /d "%~dp0.."

if not exist .env copy .env.example .env

docker compose up --build -d

echo PM app is starting on http://localhost:8000
