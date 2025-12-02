from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # product management
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.products_add, name='products_add'),
    path('products/<int:pk>/edit/', views.products_edit, name='products_edit'),
    path('products/<int:pk>/delete/', views.products_delete, name='products_delete'),
    path('products/<int:pk>/stock/', views.products_stock_update, name='products_stock_update'),
]
