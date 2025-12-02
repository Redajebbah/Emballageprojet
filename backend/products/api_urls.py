from django.urls import path
from . import api_views

urlpatterns = [
    path('<slug:slug>/', api_views.ProductDetailAPI.as_view(), name='api_product_detail'),
]
