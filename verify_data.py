#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Product, Transaction
from django.db.models import Count, Sum

print('\n' + '='*60)
print('📊 ການກວດສອບຂໍ້ມູນ (Data Verification)')
print('='*60)

# ຈຳນວນລວມ
print(f'\n✓ ຈຳນວນສິນຄ້າທັງໝົດ: {Product.objects.count()} ລາຍການ')
print(f'✓ ຈຳນວນປະຫວັດການເຄື່ອນໄຫວ: {Transaction.objects.count()} ລາຍການ')

# ປະເພດ Transaction
print(f'\n📋 ປະເພດ Transaction:')
print(f"  - ນຳເຂົ້າ (IN): {Transaction.objects.filter(transaction_type='IN').count()} ລາຍການ")
print(f"  - ຂາຍອອກ (OUT): {Transaction.objects.filter(transaction_type='OUT').count()} ລາຍການ")

# ໝວດໝູ່ສິນຄ້າ
print(f'\n📦 ໝວດໝູ່ສິນຄ້າ:')
categories = Product.objects.values('category').annotate(count=Count('id')).order_by('-count')
for cat in categories:
    print(f"  - {cat['category']}: {cat['count']} ລາຍການ")

# ສິນຄ້າທີ່ມີຢູ່ໃນສາງ
print(f'\n🏪 ສະຖານະສາງ:')
total_items = Product.objects.aggregate(total=Sum('quantity'))['total']
print(f"  ຈຳນວນສິນຄ້າລວມທັງໝົດ: {total_items} ຊິ້ນ")

# ສິນຄ້າທີ່ໃກ້ໝົດ
low_stock = Product.objects.filter(quantity__lte=5).count()
print(f"  ສິນຄ້າທີ່ໃກ້ໝົດ (<= 5): {low_stock} ລາຍການ")

# ສິນຄ້າຍອດນິຍົມ (ຂາຍດີ)
print(f'\n🔥 ສິນຄ້າຂາຍດີ TOP 5:')
top_products = Transaction.objects.filter(transaction_type='OUT').values('product__name').annotate(
    total_sold=Sum('amount')
).order_by('-total_sold')[:5]

for idx, item in enumerate(top_products, 1):
    print(f"  {idx}. {item['product__name']}: {item['total_sold']} ຊິ້ນ")

print('\n' + '='*60)
print('✅ ການກວດສອບສຳເລັດ!')
print('='*60 + '\n')
