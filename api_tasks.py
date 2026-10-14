"""TaskSet — нагрузка на REST API NordStep."""

from locust import TaskSet, task

from locust_helpers import pick_id_from_api_list, random_category_filter


class ShoeApiTaskSet(TaskSet):
    """GET-запросы к API каталога обуви."""

    @task(15)
    def api_products(self):
        self.client.get("/api/products/", name="GET /api/products/")

    @task(10)
    def api_categories(self):
        self.client.get("/api/categories/", name="GET /api/categories/")

    @task(8)
    def api_filter_categories(self):
        name = random_category_filter()
        self.client.get(
            f"/api/categories/?name={name}",
            name="GET /api/categories/?name=",
        )

    @task(6)
    def api_search_products(self):
        self.client.get(
            "/api/products/?search=runner",
            name="GET /api/products/?search=",
        )

    @task(4)
    def api_product_detail(self):
        with self.client.get(
            "/api/products/",
            name="GET /api/products/ (pick)",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"api {resp.status_code}")
                return
            try:
                item_id = pick_id_from_api_list(resp.json())
            except Exception as exc:
                resp.failure(str(exc))
                return
            if not item_id:
                resp.failure("empty api list")
                return
            resp.success()

        self.client.get(
            f"/api/products/{item_id}/",
            name="GET /api/products/<id>/",
        )
