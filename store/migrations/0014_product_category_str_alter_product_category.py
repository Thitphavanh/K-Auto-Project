from django.db import migrations, models

def copy_to_temp(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    for product in Product.objects.all():
        product.category_str = product.category
        product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category_str',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='ໝວດໝູ່ (ເກົ່າ)'),
        ),
        migrations.RunPython(copy_to_temp),
    ]
