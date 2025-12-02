from django.contrib import admin
from .models import ProductImage


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'alt', 'image')
    search_fields = ('product__name', 'alt')
