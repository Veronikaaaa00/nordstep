"""
Практическая работа №3 — Locust для магазина обуви NordStep.

TaskSet            → ShoeBrowseTaskSet, ShoeApiTaskSet (случайный выбор задач)
SequentialTaskSet  → ShoeCheckoutSequential (сценарий покупки по шагам)

Запуск UI:
  locust -f locustfile.py --host http://127.0.0.1:8000

Headless + HTML:
  locust -f locustfile.py --host http://127.0.0.1:8000 --headless -u 20 -r 4 -t 90s --html reports/locust-report.html --csv reports/locust
"""

from locust import HttpUser, between

from api_tasks import ShoeApiTaskSet
from browse_tasks import ShoeBrowseTaskSet
from sequential_tasks import ShoeCheckoutSequential


class RandomBuyer(HttpUser):
    """Случайный покупатель витрины (TaskSet)."""

    wait_time = between(0.4, 1.8)
    tasks = [ShoeBrowseTaskSet]
    weight = 3


class CheckoutBuyer(HttpUser):
    """Сценарий покупки по шагам (SequentialTaskSet)."""

    wait_time = between(0.8, 2.5)
    tasks = [ShoeCheckoutSequential]
    weight = 1


class ApiClient(HttpUser):
    """Клиент REST API каталога."""

    wait_time = between(0.3, 1.2)
    tasks = [ShoeApiTaskSet]
    weight = 2
