"""Вспомогательные функции для Locust-тестов NordStep."""

from __future__ import annotations

import random
import re
from typing import Any, Optional

from faker import Faker

fake = Faker("ru_RU")


def csrf_from_html(html: str) -> Optional[str]:
    match = re.search(
        r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']',
        html,
    )
    if match:
        return match.group(1)
    match = re.search(
        r'value=["\']([^"\']+)["\']\s+name=["\']csrfmiddlewaretoken["\']',
        html,
    )
    return match.group(1) if match else None


def pick_product_id(html: str) -> Optional[int]:
    ids = [int(x) for x in re.findall(r"/products/(\d+)/", html)]
    return random.choice(ids) if ids else None


def pick_addable_product_id(html: str) -> Optional[int]:
    """Id товаров, которые реально можно положить в корзину (есть /cart/add/)."""
    ids = [int(x) for x in re.findall(r"/cart/add/(\d+)/", html)]
    return random.choice(ids) if ids else None


def random_search_query() -> str:
    return random.choice(
        [
            "кроссовки",
            "ботинки",
            "лоферы",
            "туфли",
            "nordstep",
            "runner",
            fake.color_name(),
            fake.word(),
        ]
    )


def random_register_payload(csrf: str) -> dict[str, str]:
    username = f"{fake.user_name()}{random.randint(1000, 9999)}"
    password = fake.password(
        length=12,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    return {
        "username": username,
        "email": fake.email(),
        "password1": password,
        "password2": password,
        "csrfmiddlewaretoken": csrf,
    }


def random_checkout_comment() -> str:
    return random.choice(
        [
            fake.sentence(nb_words=6),
            "Позвоните за час до доставки",
            "Оставить у двери",
            f"Получатель: {fake.name()}",
        ]
    )


def random_category_filter() -> str:
    return random.choice(
        ["Кросс", "Бот", "Туф", "Лоф", "Санд", "Ботиль", fake.word()]
    )


def pick_id_from_api_list(payload: Any) -> Optional[int]:
    if isinstance(payload, dict):
        results = payload.get("results", [])
    elif isinstance(payload, list):
        results = payload
    else:
        return None
    if not results:
        return None
    item = random.choice(results)
    return item.get("id") if isinstance(item, dict) else None
