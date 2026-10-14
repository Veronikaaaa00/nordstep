from decimal import Decimal
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from shop.models import Category, Order, OrderItem, Product


class Command(BaseCommand):
    help = "Заполняет каталог NordStep обувью"

    def add_arguments(self, parser):
        parser.add_argument("--products", type=int, default=90)
        parser.add_argument("--reset", action="store_true", help="Очистить каталог перед заполнением")

    def handle(self, *args, **options):
        fake = Faker("ru_RU")
        n_products = options["products"]

        if options["reset"]:
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@nordstep.ru", "is_staff": True, "is_superuser": True},
        )
        admin.set_password("adminpassword")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        demo, _ = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@nordstep.ru"},
        )
        demo.set_password("demopass")
        demo.save()

        category_names = [
            ("Кроссовки", "Повседневные и спортивные модели"),
            ("Ботинки", "Демисезон и зима"),
            ("Туфли", "Классика и smart casual"),
            ("Лоферы", "Мягкая посадка для города"),
            ("Сандалии", "Летняя линейка"),
            ("Ботильоны", "Женские модели на каблуке и без"),
        ]
        categories = []
        for name, desc in category_names:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
            categories.append(cat)

        brands = [
            "NordStep", "Harbor", "Mile", "Osnova", "Tract", "Lumen", "Pavement", "Field",
        ]
        models = [
            "Runner", "Trail", "City", "Forge", "Drift", "Peak", "Avenue", "Studio",
            "Classic", "Winter", "Pulse", "SoftWalk",
        ]
        materials = [
            "натуральная кожа", "замша", "текстиль", "нубук", "комбинированный материал",
        ]
        sizes = ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"]

        existing = set(Product.objects.values_list("name", flat=True))
        created = 0
        while created < n_products:
            name = f"{random.choice(brands)} {random.choice(models)} {fake.unique.random_int(100, 9999)}"
            if name in existing:
                continue
            category = random.choice(categories)
            Product.objects.create(
                name=name,
                description=(
                    f"{category.name} из материала: {random.choice(materials)}. "
                    f"{fake.sentence(nb_words=10)}"
                ),
                price=Decimal(str(random.randint(3490, 24990))),
                size=random.choice(sizes),
                in_stock=random.random() > 0.1,
                category=category,
            )
            existing.add(name)
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"NordStep готов: categories={Category.objects.count()}, "
            f"products={Product.objects.count()}"
        ))
        self.stdout.write("admin / adminpassword")
        self.stdout.write("demo / demopass")
