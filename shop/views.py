from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .cart import get_cart, save_cart
from .forms import CheckoutForm, RegisterForm
from .models import Category, Order, OrderItem, Product


def home(request):
    products = Product.objects.filter(in_stock=True).select_related("category")[:8]
    return render(
        request,
        "shop/home.html",
        {
            "products": products,
            "categories": Category.objects.all(),
            "stats": {
                "products": Product.objects.count(),
                "categories": Category.objects.count(),
                "orders": Order.objects.count(),
            },
        },
    )


def product_list(request):
    qs = Product.objects.select_related("category").order_by("-created_at")
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category")
    stock = request.GET.get("stock")

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category_id and category_id.isdigit():
        qs = qs.filter(category_id=int(category_id))
    if stock == "1":
        qs = qs.filter(in_stock=True)

    return render(
        request,
        "shop/product_list.html",
        {
            "products": qs[:60],
            "categories": Category.objects.all(),
            "q": q,
            "category_id": category_id or "",
            "stock": stock or "",
        },
    )


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk)
    related = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "related": related},
    )


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "shop/register.html"
    success_url = reverse_lazy("product_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Регистрация успешна.")
        return response


class ShopLoginView(LoginView):
    template_name = "shop/login.html"


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("home")


def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, in_stock=True)
    cart = get_cart(request)
    key = str(product.pk)
    cart[key] = cart.get(key, 0) + 1
    messages.success(request, f"«{product.name}» добавлен в корзину.")
    response = redirect(request.META.get("HTTP_REFERER", "product_list"))
    save_cart(response, cart)
    return response


def cart_detail(request):
    cart = get_cart(request)
    ids = [int(k) for k in cart.keys() if k.isdigit()]
    products = {p.id: p for p in Product.objects.filter(id__in=ids)}
    items = []
    total = Decimal("0")
    for key, qty in cart.items():
        product = products.get(int(key))
        if not product:
            continue
        line = product.price * qty
        total += line
        items.append({"product": product, "quantity": qty, "line_total": line})
    return render(
        request,
        "shop/cart.html",
        {"items": items, "total": total, "form": CheckoutForm()},
    )


@login_required
def checkout(request):
    if request.method != "POST":
        return redirect("cart_detail")

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Проверьте данные заказа.")
        return redirect("cart_detail")

    cart = get_cart(request)
    if not cart:
        messages.error(request, "Корзина пуста.")
        return redirect("cart_detail")

    ids = [int(k) for k in cart.keys() if k.isdigit()]
    products = {
        p.id: p for p in Product.objects.filter(id__in=ids, in_stock=True)
    }
    if not products:
        messages.error(request, "Нет доступных товаров.")
        return redirect("cart_detail")

    order = Order.objects.create(
        user=request.user,
        comment=form.cleaned_data.get("comment", ""),
        total_price=0,
    )
    total = Decimal("0")
    for key, qty in cart.items():
        product = products.get(int(key))
        if not product:
            continue
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            price=product.price,
        )
        total += product.price * qty
    order.total_price = total
    order.save()

    messages.success(request, f"Заказ #{order.pk} оформлен.")
    response = redirect("order_list")
    save_cart(response, {})
    return response


@login_required
def order_list(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "shop/orders.html", {"orders": orders})


def about(request):
    return render(request, "shop/about.html")
