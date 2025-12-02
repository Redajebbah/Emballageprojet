# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Cart actions first so 'cart' does not match the '<slug>' route
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),

    path('', views.product_list, name='product_list'),          # Liste de tous les produits
    path('<int:pk>/sizes/', views.product_sizes, name='product_sizes'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),  # Détails d'un produit
]
