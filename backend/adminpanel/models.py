from django.db import models
from products.models import Product


class ProductImage(models.Model):
    """Store additional images for products without changing the original Product model."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='extra_images')
    image = models.ImageField(upload_to='adminpanel/product_images/')
    alt = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Image for {self.product.name} ({self.pk})"
