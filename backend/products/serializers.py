from rest_framework import serializers

from .models import Product


class CategoryBriefSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'image',
            'price',
            'description',
            'size',
            'stock_quantity',
            'in_stock',
            'category',
        ]

    def get_category(self, obj):
        if obj.category:
            return {'name': obj.category.name, 'slug': getattr(obj.category, 'slug', '')}
        return None

    def get_image(self, obj):
        # prefer primary image. return absolute URL if possible
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None
