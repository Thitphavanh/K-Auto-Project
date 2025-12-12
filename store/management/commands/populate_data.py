from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Brand, Product, Transaction
from decimal import Decimal
from datetime import datetime, timedelta
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
import os


class Command(BaseCommand):
    help = 'ເພີ່ມຂໍ້ມູນຕົວຈິງສຳລັບລະບົບຄຸ້ມຄອງອາໄຫຼ່ລົດ'

    def create_product_image(self, product_name, category, brand_name=None):
        """ສ້າງຮູບພາບ placeholder ສຳລັບສິນຄ້າ"""
        # ກຳນົດສີຕາມໝວດໝູ່
        colors = {
            'ຜ້າເບຣກ': ('#FF6B6B', '#FFFFFF'),  # ແດງ
            'ນ້ຳມັນເຄື່ອງ': ('#4ECDC4', '#FFFFFF'),  # ຟ້າເຂັ້ມ
            'ໄຟກາຈຸດ': ('#FFE66D', '#000000'),  # ເຫຼືອງ
            'ຟິວເຕີ': ('#95E1D3', '#000000'),  # ຟ້າອ່ອນ
            'ແບັດເຕີຣີ': ('#F38181', '#FFFFFF'),  # ບົວ
            'ຢາງລົດ': ('#2C3E50', '#FFFFFF'),  # ດຳເທົາ
            'ໄຟລົດ': ('#F9CA24', '#000000'),  # ເຫຼືອງທອງ
            'ລະບົບນ້ຳມັນ': ('#6C5CE7', '#FFFFFF'),  # ມ່ວງ
        }

        bg_color, text_color = colors.get(category, ('#95A5A6', '#FFFFFF'))

        # ສ້າງຮູບພາບ 800x600
        width, height = 800, 600
        image = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(image)

        # ວາດກ່ອງສີ່ຫຼ່ຽມຂ້າງລຸ່ມ (ສຳລັບຂໍ້ມູນ)
        overlay_height = 200
        overlay_color = tuple(max(0, c - 30) for c in Image.new('RGB', (1, 1), bg_color).getpixel((0, 0)))
        draw.rectangle([(0, height - overlay_height), (width, height)], fill=overlay_color)

        # ວາດໄອຄອນກ່ອງ (ຕົວແທນສິນຄ້າ)
        icon_size = 200
        icon_x = (width - icon_size) // 2
        icon_y = 150

        # ວາດກ່ອງສີ່ຫຼ່ຽມມົນ (ໄອຄອນ)
        padding = 20
        draw.rounded_rectangle(
            [(icon_x, icon_y), (icon_x + icon_size, icon_y + icon_size)],
            radius=20,
            fill=text_color,
            outline=text_color,
            width=3
        )

        # ວາດສັນຍາລັກ "📦"
        try:
            # ພະຍາຍາມໃຊ້ font ລະບົບ
            font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 80)
            font_medium = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 40)
            font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 30)
        except:
            # ຖ້າບໍ່ມີ font ກໍໃຊ້ default
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # ຂຽນຊື່ສິນຄ້າ (ຫຍໍ້)
        short_name = product_name[:25] + "..." if len(product_name) > 25 else product_name

        # ຄຳນວນຕຳແໜ່ງກາງ
        name_bbox = draw.textbbox((0, 0), short_name, font=font_medium)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = (width - name_width) // 2
        name_y = height - 150

        # ຂຽນຂໍ້ຄວາມ
        draw.text((name_x, name_y), short_name, fill=text_color, font=font_medium)

        # ຂຽນໜວດໝູ່
        if brand_name:
            info_text = f"{category} • {brand_name}"
        else:
            info_text = category

        info_bbox = draw.textbbox((0, 0), info_text, font=font_small)
        info_width = info_bbox[2] - info_bbox[0]
        info_x = (width - info_width) // 2
        info_y = height - 80

        draw.text((info_x, info_y), info_text, fill=text_color, font=font_small)

        # ບັນທຶກເປັນ bytes
        buffer = BytesIO()
        image.save(buffer, format='PNG', quality=95)
        buffer.seek(0)

        return buffer

    def handle(self, *_args, **_options):
        self.stdout.write(self.style.SUCCESS('ກຳລັງເພີ່ມຂໍ້ມູນ...'))

        # ສ້າງ User ຖ້າຍັງບໍ່ມີ
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@kauto.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ ສ້າງ User: {user.username}'))
        else:
            self.stdout.write(f'  User ມີຢູ່ແລ້ວ: {user.username}')

        # ສ້າງຍີ່ຫໍ້ (Brands)
        self.stdout.write('\nກຳລັງສ້າງຍີ່ຫໍ້...')
        brands_data = [
            'Toyota',
            'Honda',
            'Ford',
            'Isuzu',
            'Mitsubishi',
            'Shell',
            'Castrol',
            'Mobil',
            'NGK',
            'Denso',
            '3K',
            'GS',
            'Panasonic',
            'Bridgestone',
            'Michelin',
            'Yokohama',
            'Bosch',
            'Generic'  # ສຳລັບສິນຄ້າທົ່ວໄປທີ່ບໍ່ມີຍີ່ຫໍ້ສະເພາະ
        ]

        brands = {}
        for brand_name in brands_data:
            brand, created = Brand.objects.get_or_create(name=brand_name)
            brands[brand_name] = brand
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ ສ້າງຍີ່ຫໍ້: {brand_name}'))
            else:
                self.stdout.write(f'  ຍີ່ຫໍ້ມີຢູ່ແລ້ວ: {brand_name}')

        self.stdout.write(self.style.SUCCESS(f'✓ ສ້າງຍີ່ຫໍ້ທັງໝົດ: {len(brands_data)} ລາຍການ\n'))

        # ລາຍການອາໄຫຼ່ລົດທີ່ນິຍົມ
        products_data = [
            # ໝວດຜ້າເບຣກ (Brake Pads)
            {
                'barcode': 'BP001',
                'name': 'ຜ້າເບຣກໜ້າ Toyota Vios',
                'category': 'ຜ້າເບຣກ',
                'brand': 'Toyota',
                'cost_price': Decimal('180000'),
                'sell_price': Decimal('250000'),
                'description': 'ຜ້າເບຣກໜ້າ ສຳລັບ Toyota Vios ທຸກລຸ້ນ, ຄຸນນະພາບສູງ'
            },
            {
                'barcode': 'BP002',
                'name': 'ຜ້າເບຣກຫຼັງ Honda City',
                'category': 'ຜ້າເບຣກ',
                'brand': 'Honda',
                'cost_price': Decimal('150000'),
                'sell_price': Decimal('220000'),
                'description': 'ຜ້າເບຣກຫຼັງ Honda City ຄຸນນະພາບດີ ທົນທານ'
            },
            {
                'barcode': 'BP003',
                'name': 'ຜ້າເບຣກໜ້າ Ford Ranger',
                'category': 'ຜ້າເບຣກ',
                'brand': 'Ford',
                'cost_price': Decimal('280000'),
                'sell_price': Decimal('380000'),
                'description': 'ຜ້າເບຣກໜ້າ Ford Ranger, ເໝາະສຳລັບລົດກະບະ'
            },

            # ໝວດນ້ຳມັນເຄື່ອງ (Engine Oil)
            {
                'barcode': 'OIL001',
                'name': 'ນ້ຳມັນເຄື່ອງ Shell Helix 10W-40 4L',
                'category': 'ນ້ຳມັນເຄື່ອງ',
                'brand': 'Shell',
                'cost_price': Decimal('280000'),
                'sell_price': Decimal('350000'),
                'description': 'ນ້ຳມັນເຄື່ອງ Shell Helix ຄຸນນະພາບສູງ 4 ລິດ'
            },
            {
                'barcode': 'OIL002',
                'name': 'ນ້ຳມັນເຄື່ອງ Castrol GTX 5W-30 4L',
                'category': 'ນ້ຳມັນເຄື່ອງ',
                'brand': 'Castrol',
                'cost_price': Decimal('320000'),
                'sell_price': Decimal('420000'),
                'description': 'ນ້ຳມັນເຄື່ອງ Castrol GTX ເທີບູ 4 ລິດ'
            },
            {
                'barcode': 'OIL003',
                'name': 'ນ້ຳມັນເຄື່ອງ Mobil 1 0W-40 4L',
                'category': 'ນ້ຳມັນເຄື່ອງ',
                'brand': 'Mobil',
                'cost_price': Decimal('450000'),
                'sell_price': Decimal('580000'),
                'description': 'ນ້ຳມັນເຄື່ອງ Mobil 1 ສັງເຄາະ 100% ຄຸນນະພາບສູງສຸດ'
            },

            # ໝວດໄຟກາຈຸດ (Spark Plugs)
            {
                'barcode': 'SP001',
                'name': 'ໄຟກາຈຸດ NGK Iridium (ຊຸດ 4 ອັນ)',
                'category': 'ໄຟກາຈຸດ',
                'brand': 'NGK',
                'cost_price': Decimal('280000'),
                'sell_price': Decimal('380000'),
                'description': 'ໄຟກາຈຸດ NGK Iridium ຄຸນນະພາບເກັ່ງ ອາຍຸຍືນ'
            },
            {
                'barcode': 'SP002',
                'name': 'ໄຟກາຈຸດ Denso Platinum (ຊຸດ 4 ອັນ)',
                'category': 'ໄຟກາຈຸດ',
                'brand': 'Denso',
                'cost_price': Decimal('220000'),
                'sell_price': Decimal('300000'),
                'description': 'ໄຟກາຈຸດ Denso Platinum ເໝາະສຳລັບລົດຍີ່ປຸ່ນ'
            },

            # ໝວດຟິວເຕີນ້ຳມັນ (Oil Filters)
            {
                'barcode': 'OF001',
                'name': 'ຟິວເຕີນ້ຳມັນເຄື່ອງ Toyota',
                'category': 'ຟິວເຕີ',
                'brand': 'Toyota',
                'cost_price': Decimal('35000'),
                'sell_price': Decimal('55000'),
                'description': 'ຟິວເຕີນ້ຳມັນເຄື່ອງແທ້ Toyota'
            },
            {
                'barcode': 'OF002',
                'name': 'ຟິວເຕີນ້ຳມັນເຄື່ອງ Honda',
                'category': 'ຟິວເຕີ',
                'brand': 'Honda',
                'cost_price': Decimal('40000'),
                'sell_price': Decimal('60000'),
                'description': 'ຟິວເຕີນ້ຳມັນເຄື່ອງແທ້ Honda'
            },
            {
                'barcode': 'AF001',
                'name': 'ຟິວເຕີອາກາດ Toyota Vios',
                'category': 'ຟິວເຕີ',
                'brand': 'Toyota',
                'cost_price': Decimal('45000'),
                'sell_price': Decimal('70000'),
                'description': 'ຟິວເຕີອາກາດແທ້ Toyota Vios'
            },

            # ໝວດແບັດເຕີຣີ (Batteries)
            {
                'barcode': 'BAT001',
                'name': 'ແບັດເຕີຣີລົດຍົນ 3K 55B24L 50Ah',
                'category': 'ແບັດເຕີຣີ',
                'brand': '3K',
                'cost_price': Decimal('580000'),
                'sell_price': Decimal('750000'),
                'description': 'ແບັດເຕີຣີ 3K 50Ah ເໝາະສຳລັບລົດເກັ່ງ'
            },
            {
                'barcode': 'BAT002',
                'name': 'ແບັດເຕີຣີລົດຍົນ GS 75D23L 65Ah',
                'category': 'ແບັດເຕີຣີ',
                'brand': 'GS',
                'cost_price': Decimal('780000'),
                'sell_price': Decimal('950000'),
                'description': 'ແບັດເຕີຣີ GS 65Ah ເໝາະສຳລັບລົດກະບະ'
            },
            {
                'barcode': 'BAT003',
                'name': 'ແບັດເຕີຣີລົດຍົນ Panasonic 80D26L 70Ah',
                'category': 'ແບັດເຕີຣີ',
                'brand': 'Panasonic',
                'cost_price': Decimal('1200000'),
                'sell_price': Decimal('1450000'),
                'description': 'ແບັດເຕີຣີ Panasonic ຄຸນນະພາບສູງ 70Ah'
            },

            # ໝວດຢາງລົດ (Tires)
            {
                'barcode': 'TR001',
                'name': 'ຢາງລົດ Bridgestone 185/65R15',
                'category': 'ຢາງລົດ',
                'brand': 'Bridgestone',
                'cost_price': Decimal('850000'),
                'sell_price': Decimal('1100000'),
                'description': 'ຢາງລົດ Bridgestone ເໝາະສຳລັບລົດເກັ່ງ'
            },
            {
                'barcode': 'TR002',
                'name': 'ຢາງລົດ Michelin 215/60R16',
                'category': 'ຢາງລົດ',
                'brand': 'Michelin',
                'cost_price': Decimal('1200000'),
                'sell_price': Decimal('1500000'),
                'description': 'ຢາງລົດ Michelin ຄຸນນະພາບສູງ SUV'
            },
            {
                'barcode': 'TR003',
                'name': 'ຢາງລົດ Yokohama 265/65R17',
                'category': 'ຢາງລົດ',
                'brand': 'Yokohama',
                'cost_price': Decimal('1500000'),
                'sell_price': Decimal('1900000'),
                'description': 'ຢາງລົດ Yokohama ເໝາະສຳລັບລົດກະບະ'
            },

            # ໝວດໄຟລົດ (Lights)
            {
                'barcode': 'LT001',
                'name': 'ໜອນໄຟ LED H4 6000K (ຄູ່)',
                'category': 'ໄຟລົດ',
                'brand': 'Generic',
                'cost_price': Decimal('380000'),
                'sell_price': Decimal('520000'),
                'description': 'ໜອນໄຟ LED H4 ແສງສະຫວ່າງ ປະຫຍັດໄຟ'
            },
            {
                'barcode': 'LT002',
                'name': 'ໜອນໄຟ HID H7 8000K (ຄູ່)',
                'category': 'ໄຟລົດ',
                'brand': 'Generic',
                'cost_price': Decimal('450000'),
                'sell_price': Decimal('650000'),
                'description': 'ໜອນໄຟ HID H7 ແສງສີຂາວສະຫວ່າງ'
            },

            # ໝວດຄາບູເຣເຕີ & ລະບົບນ້ຳມັນ
            {
                'barcode': 'CB001',
                'name': 'ປັ໊ມນ້ຳມັນເຊື້ອໄຟ Toyota Hilux',
                'category': 'ລະບົບນ້ຳມັນ',
                'brand': 'Toyota',
                'cost_price': Decimal('850000'),
                'sell_price': Decimal('1200000'),
                'description': 'ປັ໊ມນ້ຳມັນເຊື້ອໄຟແທ້ Toyota Hilux'
            },
            {
                'barcode': 'CB002',
                'name': 'ຫົວຈ່າຍນ້ຳມັນ (Fuel Injector) Honda (1 ອັນ)',
                'category': 'ລະບົບນ້ຳມັນ',
                'brand': 'Honda',
                'cost_price': Decimal('280000'),
                'sell_price': Decimal('380000'),
                'description': 'ຫົວຈ່າຍນ້ຳມັນແທ້ Honda'
            },
        ]

        # ເພີ່ມສິນຄ້າ
        self.stdout.write('\nກຳລັງເພີ່ມສິນຄ້າ...')
        products = []
        for data in products_data:
            # ຫາ brand object
            brand_obj = brands.get(data.get('brand')) if data.get('brand') else None

            product, created = Product.objects.get_or_create(
                barcode=data['barcode'],
                defaults={
                    'name': data['name'],
                    'category': data['category'],
                    'brand': brand_obj,
                    'cost_price': data['cost_price'],
                    'sell_price': data['sell_price'],
                    'description': data.get('description', ''),
                    'quantity': 0  # ເລີ່ມຈາກ 0, ຈະເພີ່ມຜ່ານ Transaction
                }
            )

            # ສ້າງຮູບພາບສຳລັບສິນຄ້າ (ຖ້າຍັງບໍ່ມີ)
            if not product.image:
                try:
                    image_buffer = self.create_product_image(
                        product_name=data['name'],
                        category=data['category'],
                        brand_name=brand_obj.name if brand_obj else None
                    )

                    # ບັນທຶກຮູບພາບ
                    image_filename = f"{data['barcode']}.png"
                    product.image.save(image_filename, ContentFile(image_buffer.read()), save=True)
                    self.stdout.write(f'  📸 ສ້າງຮູບພາບ: {image_filename}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  ບໍ່ສາມາດສ້າງຮູບພາບ: {str(e)}'))

            if created:
                products.append(product)
                brand_name = data.get('brand', 'N/A')
                self.stdout.write(self.style.SUCCESS(f'✓ ເພີ່ມສິນຄ້າ: {product.name} [{brand_name}]'))
            else:
                # ອັບເດດ brand ສຳລັບສິນຄ້າທີ່ມີຢູ່ແລ້ວ
                if brand_obj and not product.brand:
                    product.brand = brand_obj
                    product.save()
                    self.stdout.write(f'  ອັບເດດຍີ່ຫໍ້: {product.name} [{brand_obj.name}]')
                else:
                    self.stdout.write(f'  ສິນຄ້າມີຢູ່ແລ້ວ: {product.name}')
                products.append(product)

        self.stdout.write(self.style.SUCCESS(f'\n✓ ເພີ່ມສິນຄ້າທັງໝົດ: {len(products_data)} ລາຍການ\n'))

        # ສ້າງ Transaction ຕົວຢ່າງ
        self.stdout.write('ກຳລັງສ້າງປະຫວັດການເຄື່ອນໄຫວ...')

        # ລຶບ Transaction ເກົ່າອອກ (ຖ້າຕ້ອງການເລີ່ມໃໝ່)
        Transaction.objects.all().delete()

        transactions_created = 0
        today = datetime.now()

        for product in products:
            # ສ້າງການນຳເຂົ້າ (IN) ໃນອາທິດທີ່ຜ່ານມາ
            for i in range(random.randint(1, 3)):
                days_ago = random.randint(1, 7)
                quantity_in = random.randint(10, 50)

                transaction = Transaction.objects.create(
                    product=product,
                    user=user,
                    transaction_type='IN',
                    amount=quantity_in,
                    total_value=product.cost_price * quantity_in
                )
                # ປັບວັນທີໃຫ້ເປັນອະດີດ
                transaction.created_at = today - timedelta(days=days_ago)
                transaction.save()

                # ອັບເດດຈຳນວນສິນຄ້າ
                product.quantity += quantity_in
                product.save()

                transactions_created += 1

            # ສ້າງການຂາຍອອກ (OUT) ບາງສ່ວນ
            if product.quantity > 5:
                for i in range(random.randint(1, 5)):
                    days_ago = random.randint(0, 6)
                    max_sell = min(product.quantity, 10)
                    if max_sell > 0:
                        quantity_out = random.randint(1, max_sell)

                        transaction = Transaction.objects.create(
                            product=product,
                            user=user,
                            transaction_type='OUT',
                            amount=quantity_out,
                            total_value=product.sell_price * quantity_out
                        )
                        # ປັບວັນທີໃຫ້ເປັນອະດີດ
                        transaction.created_at = today - timedelta(days=days_ago)
                        transaction.save()

                        # ລົບຈຳນວນສິນຄ້າ
                        product.quantity -= quantity_out
                        product.save()

                        transactions_created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ ສ້າງປະຫວັດການເຄື່ອນໄຫວ: {transactions_created} ລາຍການ\n'))

        # ສະຫຼຸບຜົນ
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('ສຳເລັດການເພີ່ມຂໍ້ມູນ! 🎉'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(f'🏷️  ຈຳນວນຍີ່ຫໍ້: {Brand.objects.count()} ລາຍການ')
        self.stdout.write(f'📦 ຈຳນວນສິນຄ້າທັງໝົດ: {Product.objects.count()} ລາຍການ')
        self.stdout.write(f'📋 ຈຳນວນປະຫວັດການເຄື່ອນໄຫວ: {Transaction.objects.count()} ລາຍການ')
        self.stdout.write(f'👤 ຈຳນວນຜູ້ໃຊ້: {User.objects.count()} ຄົນ')
        self.stdout.write(self.style.SUCCESS('=' * 60))

        # ສະແດງສິນຄ້າທີ່ມີຢູ່
        self.stdout.write('\n📊 ລາຍການສິນຄ້າທີ່ມີຢູ່ໃນສາງ:')
        self.stdout.write('-' * 100)
        self.stdout.write(f"{'ລະຫັດ':<10} {'ຊື່ສິນຄ້າ':<35} {'ຍີ່ຫໍ້':<15} {'ຈຳນວນ':<10} {'ລາຄາຂາຍ':>15}")
        self.stdout.write('-' * 100)
        for product in Product.objects.select_related('brand').all().order_by('-quantity'):
            brand_name = product.brand.name if product.brand else 'N/A'
            self.stdout.write(
                f"{product.barcode:<10} "
                f"{product.name[:35]:<35} "
                f"{brand_name:<15} "
                f"{product.quantity:<10} "
                f"{product.sell_price:>15,.0f} ກີບ"
            )
        self.stdout.write('-' * 100)
