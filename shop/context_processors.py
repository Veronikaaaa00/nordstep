from .cart import get_cart


def cart_count(request):
    cart = get_cart(request)
    return {"cart_count": sum(cart.values())}
