# NordStep

Онлайн-магазин обуви на Django + REST API.

## Запуск

```powershell
cd C:\Users\user\Desktop\loadtest-shop
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py seed_shop --reset
python manage.py runserver 0.0.0.0:8000
```

Сайт: http://127.0.0.1:8000  
API: http://127.0.0.1:8000/api/products/

Логины: `demo` / `demopass`, `admin` / `adminpassword`

## Locust (практика №3)

```powershell
pip install -r requirements-locust.txt
locust -f locustfile.py --host http://127.0.0.1:8000
```

UI: http://localhost:8089

Headless-прогон с HTML-отчётом:

```powershell
locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 20 -r 4 -t 90s --html reports/locust-report.html --csv reports/locust
```
