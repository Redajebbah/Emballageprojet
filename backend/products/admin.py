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
    list_display = ('id', 'name', 'category', 'price', 'stock_quantity', 'in_stock', 'slug')
    list_filter = ('category', 'in_stock')
    search_fields = ('name', 'slug', 'category__name')
    ordering = ('-id',)
    readonly_fields = ('slug',)
    list_editable = ('stock_quantity', 'in_stock')

    # Enable ProductSize inline first so sizes appear in the product edit page.
    class ProductSizeInline(admin.TabularInline):
        model = ProductSize
        extra = 1

    if ProductImage:
        inlines = (ProductSizeInline, ProductImageInline)
    else:
        inlines = (ProductSizeInline,)

    actions = ['mark_in_stock', 'mark_out_of_stock']

    def mark_in_stock(self, request, queryset):
        queryset.update(in_stock=True)
        self.message_user(request, "Selected products marked as in stock.")

    mark_in_stock.short_description = 'Marquer comme en stock'

    def mark_out_of_stock(self, request, queryset):
        queryset.update(in_stock=False, stock_quantity=0)
        self.message_user(request, "Selected products marked out of stock (quantity set to 0).")

    mark_out_of_stock.short_description = 'Marquer comme en rupture (stock 0)'
from django.contrib import admin

# Register your models here.
