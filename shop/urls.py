from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_list, name="order_list"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.ShopLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
