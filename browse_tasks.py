"""
TaskSet — случайный покупатель NordStep.

Задачи выбираются случайно по весам @task(N).
GET: 12+10+8+7+6 = 43
POST: 2+2+1 = 5
→ GET примерно в 8.6 раз чаще POST (>= 5).
"""

from locust import TaskSet, task

from locust_helpers import (
    csrf_from_html,
    pick_addable_product_id,
    pick_product_id,
    random_checkout_comment,
    random_register_payload,
    random_search_query,
)


class ShoeBrowseTaskSet(TaskSet):
    """Случайный обход витрины и редкие POST."""

    @task(12)
    def open_home(self):
        self.client.get("/", name="GET /")

    @task(10)
    def open_catalog(self):
        self.client.get("/products/", name="GET /products/")

    @task(8)
    def search_shoes(self):
        query = random_search_query()
        self.client.get(f"/products/?q={query}", name="GET /products/?q=")

    @task(7)
    def open_api_products(self):
        self.client.get("/api/products/", name="GET /api/products/")

    @task(6)
    def open_product_detail(self):
        with self.client.get(
            "/products/",
            name="GET /products/ (for detail)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"catalog {resp.status_code}")
                return
            product_id = pick_product_id(resp.text)
            if not product_id:
                resp.failure("no product ids")
                return
            resp.success()
        self.client.get(f"/products/{product_id}/", name="GET /products/<id>/")

    @task(2)
    def login_demo(self):
        with self.client.get("/login/", name="GET /login/", catch_response=True) as page:
            token = csrf_from_html(page.text) if page.status_code == 200 else None
            if not token:
                page.failure("no csrf on login")
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
            name="POST /login/",
        )

    @task(2)
    def checkout_order(self):
        with self.client.get(
            "/login/",
            catch_response=True,
            name="GET /login/ (checkout)",
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
            name="POST /login/ (before checkout)",
        )

        with self.client.get(
            "/products/?stock=1",
            catch_response=True,
            name="GET /products/ (cart)",
        ) as cat:
            product_id = pick_addable_product_id(cat.text) if cat.status_code == 200 else None
            if not product_id:
                cat.failure("no products in stock")
                return
            cat.success()

        with self.client.get(
            f"/cart/add/{product_id}/",
            name="GET /cart/add/<id>/",
            catch_response=True,
        ) as add_resp:
            if add_resp.status_code >= 400:
                add_resp.failure(f"add failed {add_resp.status_code}")
                return
            add_resp.success()

        with self.client.get("/cart/", catch_response=True, name="GET /cart/") as cart_page:
            csrf = csrf_from_html(cart_page.text) if cart_page.status_code == 200 else None
            if not csrf:
                cart_page.failure("no csrf on cart")
                return
            cart_page.success()

        self.client.post(
            "/cart/checkout/",
            data={
                "csrfmiddlewaretoken": csrf,
                "comment": random_checkout_comment(),
            },
            headers={"Referer": f"{self.client.base_url}/cart/"},
            name="POST /cart/checkout/",
        )

    @task(1)
    def register_user(self):
        with self.client.get(
            "/register/",
            catch_response=True,
            name="GET /register/",
        ) as page:
            token = csrf_from_html(page.text) if page.status_code == 200 else None
            if not token:
                page.failure("no csrf on register")
                return
            page.success()

        self.client.post(
            "/register/",
            data=random_register_payload(token),
            headers={"Referer": f"{self.client.base_url}/register/"},
            name="POST /register/",
        )
