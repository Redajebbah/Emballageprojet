from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=64, help_text='Human label for the size, e.g. "10x14"')),
                ('price', models.DecimalField(max_digits=10, decimal_places=2)),
                ('stock', models.PositiveIntegerField(blank=True, null=True, default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sizes', to='products.product')),
            ],
            options={
                'ordering': ['product', 'label'],
                'unique_together': {('product', 'label')},
            },
        ),
    ]
