from django.contrib import admin
from .models import Product, ProductSize

try:
    # optional inline from adminpanel if installed
    from adminpanel.models import ProductImage
except Exception:
    ProductImage = None


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('__str__',) if ProductImage else ()


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

    if ProductImage:
        inlines = (ProductSizeInline, ProductImageInline)
    else:
        inlines = (ProductSizeInline,)
