from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count, Sum

from products.models import Product
from categories.models import Category
from .models import ProductImage
from .forms import AdminLoginForm, ProductForm, StockUpdateForm
from .decorators import admin_required


def admin_login(request):
    if request.user.is_authenticated and (request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('adminpanel:dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['password']
            user = User.objects.filter(email=email).first()
            if user and user.check_password(pwd) and (user.groups.filter(name='admin').exists() or user.is_superuser):
                auth_login(request, user)
                next_url = request.GET.get('next') or reverse('adminpanel:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Email ou mot de passe invalide, ou pas autorisé.')
    else:
        form = AdminLoginForm()

    return render(request, 'adminpanel/login.html', {'form': form})


def admin_logout(request):
    auth_logout(request)
    return redirect(reverse('adminpanel:login'))


@admin_required
def dashboard(request):
    total_products = Product.objects.count()
    out_of_stock = Product.objects.filter(in_stock=False).count()
    total_categories = Category.objects.count()
    total_stock = Product.objects.aggregate(total=Sum('stock_quantity'))['total'] or 0

    # top products by lowest stock
    top_low_stock = Product.objects.order_by('stock_quantity')[:8]

    # categories vs product counts
    categories_data = Category.objects.annotate(count=Count('products'))

    return render(request, 'adminpanel/dashboard.html', {
        'total_products': total_products,
        'out_of_stock': out_of_stock,
        'total_categories': total_categories,
        'total_stock': total_stock,
        'top_low_stock': top_low_stock,
        'categories_data': categories_data,
    })


@admin_required
def products_list(request):
    q = request.GET.get('q', '')
    products = Product.objects.select_related('category').all()
    if q:
        products = products.filter(name__icontains=q)

    return render(request, 'adminpanel/products_list.html', {'products': products, 'q': q})


@admin_required
def products_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            # ensure slug is generated as in model save
            prod.save()
            # handle images
            files = request.FILES.getlist('images')
            for f in files:
                ProductImage.objects.create(product=prod, image=f)
            messages.success(request, 'Produit ajouté avec succès')
            return redirect('adminpanel:products_list')
    else:
        form = ProductForm()

    return render(request, 'adminpanel/product_form.html', {'form': form, 'is_add': True})


@admin_required
def products_edit(request, pk):
    prod = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            prod = form.save()
            files = request.FILES.getlist('images')
            for f in files:
                ProductImage.objects.create(product=prod, image=f)
            messages.success(request, 'Produit mis à jour')
            return redirect('adminpanel:products_list')
    else:
        form = ProductForm(instance=prod)

    images = prod.extra_images.all()
    return render(request, 'adminpanel/product_form.html', {'form': form, 'product': prod, 'images': images, 'is_add': False})


@admin_required
def products_delete(request, pk):
    prod = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        prod.delete()
        messages.success(request, 'Produit supprimé')
        return redirect('adminpanel:products_list')

    return render(request, 'adminpanel/product_confirm_delete.html', {'product': prod})


@admin_required
def products_stock_update(request, pk):
    """Update stock via a small form on list."""
    prod = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            prod.stock_quantity = form.cleaned_data['stock']
            prod.in_stock = prod.stock_quantity > 0
            prod.save()
            messages.success(request, 'Stock mis à jour')
    return redirect('adminpanel:products_list')
