from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # populate slug on save if blank
        if not self.slug:
            base = slugify(self.name) or 'category'
            candidate = base
            suffix = 1
            # ensure uniqueness
            while Category.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{suffix}"
                suffix += 1
            self.slug = candidate

        super().save(*args, **kwargs)
