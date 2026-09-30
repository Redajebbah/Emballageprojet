from django.conf import settings
from django.db.models import Count

from categories.models import Category


def contact_info(request):
    """Expose shop contact details and the category menu to all templates."""
    return {
        'WHATSAPP_NUMBER': settings.WHATSAPP_NUMBER,
        'CONTACT_PHONES': ['06 58 28 32 77', '06 45 55 71 22'],
        'CONTACT_EMAIL': 'emboitage@contact.ma',
        'INSTAGRAM_URL': 'https://www.instagram.com/emboitage/',
        'nav_categories': Category.objects.annotate(product_count=Count('products')).order_by('name'),
    }
