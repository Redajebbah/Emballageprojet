# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),          # Liste de tous les produits
    path('<int:pk>/sizes/', views.product_sizes, name='product_sizes'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),  # Détails d'un produit
]
