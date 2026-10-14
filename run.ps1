$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
    .\.venv\Scripts\pip.exe install -r requirements.txt
}

.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_shop
Write-Host ""
Write-Host "Сайт: http://127.0.0.1:8000"
Write-Host "API:  http://127.0.0.1:8000/api/products/"
Write-Host "demo / demopass | admin / adminpassword"
Write-Host ""
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
