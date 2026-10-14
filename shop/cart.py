import json
import base64


def get_cart(request):
    raw = request.COOKIES.get("cart", "")
    if not raw:
        return {}
    try:
        decoded = base64.b64decode(raw.encode("utf-8")).decode("utf-8")
        data = json.loads(decoded)
        return {str(k): int(v) for k, v in data.items()}
    except Exception:
        return {}


def save_cart(response, cart):
    encoded = base64.b64encode(json.dumps(cart).encode("utf-8")).decode("utf-8")
    response.set_cookie("cart", encoded, max_age=60 * 60 * 24 * 14)
