from django.contrib import admin
from django.urls import path, include  # include doit être importé ici
from django.conf import settings
from django.conf.urls.static import static
from products import views as product_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # root homepage
    path('', product_views.home, name='home'),
    path('products/', include('products.urls')),
    # Products API (DRF)
    path('api/products/', include('products.api_urls')),
    # Friendly product detail path (client wants /product/<slug>)
    path('product/<slug:slug>/', product_views.product_detail, name='product_detail_root'),
    path('orders/', include('orders.urls')),
    # isolated management area for the project (custom adminpanel)
    path('admin-panel/', include('adminpanel.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)