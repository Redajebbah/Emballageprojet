from django.db import models
from categories.models import Category
from django.utils.text import slugify

class Product(models.Model):
    SIZE_CHOICES = [
        ("S", "Small"),
        ("M", "Medium"),
        ("L", "Large"),
        ("XL", "Extra Large"),
    ]

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    slug = models.SlugField(unique=True, blank=True)
    
    description = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, default="MAD")

    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, null=True)

    stock_quantity = models.PositiveIntegerField(default=0)
    in_stock = models.BooleanField(default=True)

    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image2 = models.ImageField(upload_to="products/", blank=True, null=True)
    image3 = models.ImageField(upload_to="products/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        # Only auto-set in_stock to False if stock_quantity is 0
        # This allows manual control when stock_quantity > 0
        if self.stock_quantity == 0:
            self.in_stock = False

        super().save(*args, **kwargs)

    def discount_percentage(self):
        """Calculate discount percentage if old_price exists"""
        if self.old_price and self.old_price > self.price:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

    def __str__(self):
        return self.name


class ProductSize(models.Model):
    """Multiple sizes/pricing for a Product. Kept separate so a product can have many sizes."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    label = models.CharField(max_length=64, help_text='Human label for the size, e.g. "10x14"')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['product', 'label']
        unique_together = ('product', 'label')

    def __str__(self):
        return f"{self.product.name} — {self.label} ({self.price})"
