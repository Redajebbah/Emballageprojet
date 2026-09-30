from urllib.parse import quote

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def whatsapp_url(context, product=None):
    """Build a wa.me link, pre-filled with the product name and page URL when given."""
    if product is None:
        message = "Bonjour, je souhaite avoir des informations sur vos produits."
    else:
        message = f"Bonjour, je suis intéressé(e) par le produit : {product.name}"
        request = context.get('request')
        if request is not None and getattr(product, 'slug', None):
            message += "\n" + request.build_absolute_uri(f"/product/{product.slug}/")
    return f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(message)}"
