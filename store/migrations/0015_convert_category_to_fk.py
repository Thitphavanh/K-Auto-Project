import django.db.models.deletion
from django.db import migrations, models

def clear_and_populate(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Category = apps.get_model('store', 'Category')
    
    # 1. Clear original category field (it's still a CharField)
    # We use a direct SQL update to be fast and avoid triggers
    Product.objects.all().update(category=None)

def finalize_migration(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    Category = apps.get_model('store', 'Category')
    
    # 2. Populate Category model and link Products
    for product in Product.objects.all():
        cat_name = product.category_str
        if cat_name:
            category, created = Category.objects.get_or_create(name=cat_name)
            product.category = category
            product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_product_category_str_alter_product_category'),
    ]

    operations = [
        # Clear data while it's still a CharField
        migrations.RunPython(clear_and_populate),
        # Now change the type to ForeignKey
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.category', verbose_name='ໝວດໝູ່'),
        ),
        # Link to the new Category objects
        migrations.RunPython(finalize_migration),
    ]
