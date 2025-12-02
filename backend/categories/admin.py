from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'has_image')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    readonly_fields = ('slug',)
    
    def has_image(self, obj):
        return "✅" if obj.image else "❌"
    has_image.short_description = 'Image'


