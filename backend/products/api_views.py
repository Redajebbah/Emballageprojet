from rest_framework import generics
from .models import Product
from .serializers import ProductDetailSerializer


class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
