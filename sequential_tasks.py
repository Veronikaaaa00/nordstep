"""
SequentialTaskSet — сценарий покупки обуви по шагам.

TaskSet:          задачи выбираются случайно по весу.
SequentialTaskSet: задачи идут строго по порядку объявления.
"""

from typing import Optional

from locust import SequentialTaskSet, task

from locust_helpers import (
    csrf_from_html,
    pick_addable_product_id,
    pick_product_id,
    random_checkout_comment,
)


class ShoeCheckoutSequential(SequentialTaskSet):
    """Последовательный сценарий: витрина → логин → корзина → заказ."""

    product_id: Optional[int] = None

    @task
    def step_home(self):
        self.client.get("/", name="SEQ GET /")

    @task
    def step_catalog(self):
        with self.client.get(
            "/products/?stock=1",
            name="SEQ GET /products/",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"status {resp.status_code}")
                return
            self.product_id = pick_addable_product_id(resp.text) or pick_product_id(resp.text)
            if not self.product_id:
                resp.failure("no product ids")
            else:
                resp.success()

    @task
    def step_detail(self):
        if not self.product_id:
            return
        self.client.get(
            f"/products/{self.product_id}/",
            name="SEQ GET /products/<id>/",
        )

    @task
    def step_login(self):
        with self.client.get(
            "/login/",
            name="SEQ GET /login/",
            catch_response=True,
        ) as page:
            token = csrf_from_html(page.text) if page.status_code == 200 else None
            if not token:
                page.failure("no csrf")
                return
            page.success()

        self.client.post(
            "/login/",
            data={
                "username": "demo",
                "password": "demopass",
                "csrfmiddlewaretoken": token,
            },
            headers={"Referer": f"{self.client.base_url}/login/"},
            name="SEQ POST /login/",
        )

    @task
    def step_add_to_cart(self):
        if not self.product_id:
            return
        with self.client.get(
            f"/cart/add/{self.product_id}/",
            name="SEQ GET /cart/add/<id>/",
            catch_response=True,
        ) as add_resp:
            if add_resp.status_code >= 400:
                add_resp.failure(f"add failed {add_resp.status_code}")
                self.product_id = None
                return
            add_resp.success()

    @task
    def step_checkout(self):
        if not self.product_id:
            return
        with self.client.get(
            "/cart/",
            name="SEQ GET /cart/",
            catch_response=True,
        ) as cart_page:
            csrf = csrf_from_html(cart_page.text) if cart_page.status_code == 200 else None
            if not csrf:
                cart_page.failure("no csrf")
                return
            cart_page.success()

        self.client.post(
            "/cart/checkout/",
            data={
                "csrfmiddlewaretoken": csrf,
                "comment": random_checkout_comment(),
            },
            headers={"Referer": f"{self.client.base_url}/cart/"},
            name="SEQ POST /cart/checkout/",
        )
