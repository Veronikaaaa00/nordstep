$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
    .\.venv\Scripts\pip.exe install -r requirements.txt
}

if (-not (Test-Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
}

Write-Host "Поднимаю PostgreSQL..."
docker compose up -d db

Write-Host "Жду готовности БД..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    docker exec nordstep-db pg_isready -U nordstep -d nordstep 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    throw "PostgreSQL не поднялся. Проверь Docker Desktop."
}

.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_shop
Write-Host ""
Write-Host "Сайт: http://127.0.0.1:8000"
Write-Host "API:  http://127.0.0.1:8000/api/products/"
Write-Host "БД:   PostgreSQL nordstep @ 127.0.0.1:5432"
Write-Host "demo / demopass | admin / adminpassword"
Write-Host ""
.\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
