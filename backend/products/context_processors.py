from django.conf import settings


def contact_info(request):
    """Expose the shop's WhatsApp number to all templates."""
    return {'WHATSAPP_NUMBER': settings.WHATSAPP_NUMBER}
