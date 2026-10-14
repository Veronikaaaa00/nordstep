from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter

from shop.models import Category, Order, Product

from .serializers import CategorySerializer, OrderSerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            qs = qs.filter(name__icontains=name)
        return qs


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related("category").order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        in_stock = self.request.query_params.get("in_stock")
        if category and category.isdigit():
            qs = qs.filter(category_id=int(category))
        if in_stock == "1":
            qs = qs.filter(in_stock=True)
        return qs


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.prefetch_related("items__product").order_by("-created_at")
        return (
            Order.objects.filter(user=user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
