from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productsize'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock_quantity',
        ),
        migrations.RemoveField(
            model_name='product',
            name='in_stock',
        ),
        migrations.RemoveField(
            model_name='productsize',
            name='stock',
        ),
    ]
