from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Order, OrderItem
from products.models import Product

def order_list(request):
    orders = Order.objects.all()
    return render(request, 'orders/order_list.html', {'orders': orders})

def order_detail(request, id):
    order = Order.objects.get(id=id)
    return render(request, 'orders/order_detail.html', {'order': order})

@csrf_exempt
@require_POST
def create_order(request):
    """Create order from cart data before WhatsApp redirect"""
    try:
        data = json.loads(request.body)
        
        # Create order
        order = Order.objects.create(
            customer_name=data.get('customer_name'),
            customer_phone=data.get('customer_phone'),
            customer_email=data.get('customer_email', ''),
            customer_city=data.get('customer_city', ''),
            customer_address=data.get('customer_address', ''),
            customer_notes=data.get('customer_notes', ''),
            total_price=data.get('total_price', 0)
        )
        
        # Create order items
        cart_items = data.get('items', [])
        for item in cart_items:
            try:
                product = Product.objects.get(slug=item['slug'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )
            except Product.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': 'Commande enregistrée avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

