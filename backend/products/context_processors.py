def cart_count(request):
    """Expose a cart item count (total quantities) to templates.

    Cart stored in session under 'cart' as a dict mapping product_id (str) to
    dict { 'name', 'price', 'image', 'quantity' }.
    """
    cart = request.session.get('cart', {})
    total_items = 0
    for item in cart.values():
        try:
            qty = int(item.get('quantity', 0))
        except Exception:
            qty = 0
        total_items += qty

    return {'cart_count': total_items}
