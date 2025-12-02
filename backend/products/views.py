# products/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Count

from .models import Product
from categories.models import Category
from decimal import Decimal
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_POST


def product_list(request):
    """Render the product list with optional category filtering.

    Accepts a query param `category=<slug>` where `slug` is the Category.slug.

    The template expects `categories` (with product_count and slug) and
    an optional `selected_category` object when filtering.
    """

    # get categories annotated with product counts
    categories = Category.objects.annotate(product_count=Count('products'))

    category_slug = request.GET.get('category')
    selected_category = None

    if category_slug:
        # find by persisted slug on the Category model
        selected_category = get_object_or_404(Category, slug=category_slug)

    # filter products by selected category (model instance) if present
    if selected_category:
        products = Product.objects.filter(category=selected_category)
    else:
        products = Product.objects.all()

    # performance: include category relationship for templates
    products = products.select_related('category')

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'categories': categories,
            'selected_category': selected_category,
        },
    )


def home(request):
    """Render the home page with a small selection of products.

    Shows a few products (e.g., popular) so homepage has content. No complex logic.
    """
    from categories.models import Category
    
    # lightweight selection for the home page
    products = Product.objects.select_related('category').all()[:8]
    
    # Get categories for showcase section
    categories = Category.objects.all()[:6]

    return render(request, 'products/home.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)

    # similar products (same category) - exclude current product
    similar_products = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]

    # Prefer the new ProductSize relation when available; fall back to the single choice size field
    sizes_qs = getattr(product, 'sizes', None)
    if sizes_qs and sizes_qs.exists():
        sizes = list(sizes_qs.all())
    else:
        sizes = []
        if product.size:
            sizes = [product.size]

    context = {
        'product': product,
        'similar_products': similar_products,
        'sizes': sizes,
    }

    return render(request, 'products/product_detail.html', context)


def product_sizes(request, pk):
    """Return a simple page listing all sizes for a product (label + price).

    This view intentionally keeps behaviour read-only and non-destructive.
    """
    product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
    sizes = product.sizes.all()

    return render(request, 'products/product_sizes.html', {'product': product, 'sizes': sizes})


# ---- Cart session helpers and views ----
def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


@require_POST
def cart_add(request):
    """Add a product to cart (session).

    Expects POST params: slug, quantity (optional)
    """
    slug = request.POST.get('slug')
    if not slug:
        return redirect(request.META.get('HTTP_REFERER', reverse('products:product_list')))

    product = get_object_or_404(Product, slug=slug)
    try:
        qty = int(request.POST.get('quantity', 1))
    except Exception:
        qty = 1
    if qty <= 0:
        qty = 1

    cart = _get_cart(request)
    pid = str(product.id)
    if pid in cart:
        cart[pid]['quantity'] = int(cart[pid].get('quantity', 0)) + qty
    else:
        cart[pid] = {
            'name': product.name,
            'slug': product.slug,
            'price': str(product.price),
            'quantity': qty,
            'image': product.image.url if product.image else '',
        }

    _save_cart(request, cart)

    # redirect back to cart page
    return redirect(reverse('products:cart_detail'))


def cart_detail(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')

    # validate product ids, convert to live objects and compute totals
    to_delete = []
    for pid, data in cart.items():
        try:
            product = Product.objects.get(pk=int(pid))
        except Exception:
            to_delete.append(pid)
            continue

        quantity = int(data.get('quantity', 0))
        price = Decimal(str(data.get('price', product.price)))
        subtotal = price * quantity
        total += subtotal

        items.append({'product': product, 'quantity': quantity, 'price': price, 'subtotal': subtotal})

    # remove missing products
    if to_delete:
        for pid in to_delete:
            cart.pop(pid, None)
        _save_cart(request, cart)

    context = {
        'cart_items': items,
        'cart_total': total,
        # show a few suggestions on the cart page; used by the include in cart.html
        'products': Product.objects.select_related('category').all()[:6],
    }
    return render(request, 'products/cart.html', context)


@require_POST
def cart_update(request):
    product_id = request.POST.get('product_id')
    try:
        quantity = int(request.POST.get('quantity', 0))
    except Exception:
        quantity = 0

    cart = _get_cart(request)
    if product_id and product_id in cart:
        if quantity <= 0:
            cart.pop(product_id, None)
        else:
            cart[product_id]['quantity'] = quantity

    _save_cart(request, cart)
    return redirect(reverse('products:cart_detail'))


@require_POST
def cart_remove(request):
    product_id = request.POST.get('product_id')
    cart = _get_cart(request)
    if product_id and product_id in cart:
        cart.pop(product_id, None)
    _save_cart(request, cart)
    return redirect(reverse('products:cart_detail'))


@require_POST
def cart_clear(request):
    request.session.pop('cart', None)
    request.session.modified = True
    return redirect(reverse('products:cart_detail'))


# Create your views here.
