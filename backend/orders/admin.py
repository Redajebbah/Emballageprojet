from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'customer_city', 'created_at', 'total_price', 'is_paid', 'payment_status')
    list_display_links = ('id', 'customer_name')
    list_filter = ('is_paid', 'created_at', 'customer_city')
    search_fields = ('customer_name', 'customer_phone', 'customer_email', 'id')
    readonly_fields = ('created_at', 'total_price')
    list_editable = ('is_paid',)
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Informations Client', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'customer_city', 'customer_address')
        }),
        ('Détails Commande', {
            'fields': ('total_price', 'created_at', 'customer_notes')
        }),
        ('Statut Paiement', {
            'fields': ('is_paid',),
            'classes': ('wide',)
        }),
    )
    
    def payment_status(self, obj):
        if obj.is_paid:
            return '✅ Payé'
        return '⏳ En attente'
    payment_status.short_description = 'Statut Paiement'

