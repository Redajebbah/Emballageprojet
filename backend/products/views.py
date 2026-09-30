# products/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, F, Q

from .models import Product
from categories.models import Category


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

    # Filter by promotion if requested
    promotion = bool(request.GET.get('promotion'))
    if promotion:
        products = products.filter(old_price__gt=F('price'))

    # Free-text search from the header search box
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q)
        )

    # performance: include category relationship for templates
    products = products.select_related('category').order_by('-id')

    return render(
        request,
        'products/product_list.html',
        {
            'products': products,
            'categories': categories,
            'selected_category': selected_category,
            'promotion': promotion,
            'q': q,
        },
    )


def home(request):
    """Render the home page with a small selection of products.

    Shows a few products (e.g., popular) so homepage has content. No complex logic.
    """
    # newest products first
    products = Product.objects.select_related('category').order_by('-id')[:8]

    # categories for the showcase section, with their product count
    categories = Category.objects.annotate(product_count=Count('products'))

    return render(request, 'products/home.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)

    # similar products (same category) - exclude current product
    similar_products = (
        Product.objects.select_related('category')
        .filter(category=product.category).exclude(pk=product.pk).order_by('-id')[:4]
    )

    # sizes with their own price (ProductSize), shown as selectable chips
    sizes = list(product.sizes.all())
    images = [img for img in (product.image, product.image2, product.image3) if img]

    context = {
        'product': product,
        'images': images,
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

