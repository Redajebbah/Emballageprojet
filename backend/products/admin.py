from django.contrib import admin
from .models import Product, ProductSize


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'slug')
    list_filter = ('category',)
    search_fields = ('name', 'slug', 'category__name')
    ordering = ('-id',)
    readonly_fields = ('slug',)

    # Enable ProductSize inline first so sizes appear in the product edit page.
    class ProductSizeInline(admin.TabularInline):
        model = ProductSize
        extra = 1

    # Photos shown on the site are the image / image2 / image3 fields.
    inlines = (ProductSizeInline,)
