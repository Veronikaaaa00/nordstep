# NordStep

Онлайн-магазин обуви на Django + PostgreSQL + REST API.

Репозиторий: https://github.com/Veronikaaaa00/nordstep

## Стек

- Django / DRF
- **PostgreSQL 16** (Docker-контейнер `nordstep-db`)
- Locust — нагрузочные тесты

## Быстрый запуск

1. Включи Docker Desktop  
2. В терминале:

```powershell
cd C:\Users\user\Desktop\loadtest-shop
.\run.ps1
```

Сайт: http://127.0.0.1:8000  
API: http://127.0.0.1:8000/api/products/

Логины: `demo` / `demopass`, `admin` / `adminpassword`

## База данных

| Параметр | Значение |
|----------|----------|
| Тип | PostgreSQL |
| Host | `127.0.0.1` |
| Port | `5432` |
| DB | `nordstep` |
| User | `nordstep` |
| Password | `nordsteppass` |
| Контейнер | `nordstep-db` |

Проверить, есть ли записи:

```powershell
docker exec -it nordstep-db psql -U nordstep -d nordstep -c "SELECT COUNT(*) FROM shop_product;"
docker exec -it nordstep-db psql -U nordstep -d nordstep -c "SELECT id, name, price FROM shop_product LIMIT 5;"
```

Или через Django:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from shop.models import Product; print(Product.objects.count())"
```

## Locust

```powershell
pip install -r requirements-locust.txt
locust -f locustfile.py --host http://127.0.0.1:8000
```

UI: http://localhost:8089
