from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import CurrencyRate, Brand, Product, Order, OrderItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'ສ້າງຂໍ້ມູນຕົວຢ່າງສຳລັບທົດສອບລະບົບ'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🚀 ກຳລັງສ້າງຂໍ້ມູນຕົວຢ່າງ...'))

        # 1. ສ້າງອັດຕາແລກປ່ຽນ
        self.create_currency_rates()

        # 2. ສ້າງຍີ່ຫໍ້
        self.create_brands()

        # 3. ສ້າງສິນຄ້າ
        self.create_products()

        # 4. ສ້າງບິນການຂາຍຕົວຢ່າງ
        self.create_orders()

        self.stdout.write(self.style.SUCCESS('✅ ສ້າງຂໍ້ມູນສຳເລັດແລ້ວ!'))

    def create_currency_rates(self):
        """ສ້າງອັດຕາແລກປ່ຽນ"""
        self.stdout.write('📊 ກຳລັງສ້າງອັດຕາແລກປ່ຽນ...')

        currencies = [
            {
                'currency_code': 'THB',
                'name': 'ບາດໄທ',
                'rate_to_thb': Decimal('1.000000'),
                'symbol': '฿'
            },
            {
                'currency_code': 'LAK',
                'name': 'ກີບລາວ',
                'rate_to_thb': Decimal('270.000000'),  # 1 THB = 270 LAK
                'symbol': '₭'
            },
            {
                'currency_code': 'USD',
                'name': 'ໂດລາສະຫະລັດ',
                'rate_to_thb': Decimal('0.029412'),  # 1 USD = 34 THB => 1 THB = 0.029412 USD
                'symbol': '$'
            },
        ]

        for curr in currencies:
            obj, created = CurrencyRate.objects.get_or_create(
                currency_code=curr['currency_code'],
                defaults={
                    'name': curr['name'],
                    'rate_to_thb': curr['rate_to_thb'],
                    'symbol': curr['symbol']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ ສ້າງ {curr["name"]} ({curr["currency_code"]})'))
            else:
                self.stdout.write(f'  - {curr["name"]} ມີຢູ່ແລ້ວ')

    def create_brands(self):
        """ສ້າງຍີ່ຫໍ້"""
        self.stdout.write('🏭 ກຳລັງສ້າງຍີ່ຫໍ້...')

        brands = ['Toyota', 'Honda', 'Nissan', 'Mazda', 'Mitsubishi']

        for brand_name in brands:
            obj, created = Brand.objects.get_or_create(name=brand_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ ສ້າງຍີ່ຫໍ້ {brand_name}'))
            else:
                self.stdout.write(f'  - ຍີ່ຫໍ້ {brand_name} ມີຢູ່ແລ້ວ')

    def create_products(self):
        """ສ້າງສິນຄ້າຕົວຢ່າງ"""
        self.stdout.write('📦 ກຳລັງສ້າງສິນຄ້າ...')

        toyota = Brand.objects.get(name='Toyota')
        honda = Brand.objects.get(name='Honda')

        products = [
            {
                'barcode': 'BRK001',
                'name': 'ຜ້າເບຣກໜ້າ Toyota Vios',
                'brand': toyota,
                'category': 'ເບຣກ',
                'cost_price': Decimal('450.00'),
                'sell_price': Decimal('650.00'),
                'quantity': 20
            },
            {
                'barcode': 'OIL001',
                'name': 'ນ້ຳມັນເຄື່ອງ 10W-40',
                'brand': None,
                'category': 'ນ້ຳມັນ',
                'cost_price': Decimal('280.00'),
                'sell_price': Decimal('380.00'),
                'quantity': 50
            },
            {
                'barcode': 'FILT001',
                'name': 'ໄສເຄື່ອງ Honda City',
                'brand': honda,
                'category': 'ໄສ',
                'cost_price': Decimal('120.00'),
                'sell_price': Decimal('180.00'),
                'quantity': 35
            },
            {
                'barcode': 'TIRE001',
                'name': 'ຢາງລົດ 195/65R15',
                'brand': None,
                'category': 'ຢາງລົດ',
                'cost_price': Decimal('1800.00'),
                'sell_price': Decimal('2200.00'),
                'quantity': 16
            },
            {
                'barcode': 'BAT001',
                'name': 'ແບັດເຕີຣີ 12V 60Ah',
                'brand': None,
                'category': 'ແບັດເຕີຣີ',
                'cost_price': Decimal('1500.00'),
                'sell_price': Decimal('1850.00'),
                'quantity': 12
            },
        ]

        for prod_data in products:
            obj, created = Product.objects.get_or_create(
                barcode=prod_data['barcode'],
                defaults={
                    'name': prod_data['name'],
                    'brand': prod_data['brand'],
                    'category': prod_data['category'],
                    'cost_price': prod_data['cost_price'],
                    'sell_price': prod_data['sell_price'],
                    'quantity': prod_data['quantity']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ ສ້າງສິນຄ້າ {prod_data["name"]}'))
            else:
                self.stdout.write(f'  - {prod_data["name"]} ມີຢູ່ແລ້ວ')

    def create_orders(self):
        """ສ້າງບິນການຂາຍຕົວຢ່າງ"""
        self.stdout.write('📄 ກຳລັງສ້າງບິນການຂາຍ...')

        # ເອົາ user ທຳອິດມາໃຊ້ (ຖ້າບໍ່ມີກໍ່ສ້າງ superuser)
        user = User.objects.first()
        if not user:
            user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.WARNING('  ⚠️ ສ້າງ superuser: admin/admin123'))

        # ເອົາອັດຕາແລກປ່ຽນ
        lak_rate = CurrencyRate.objects.get(currency_code='LAK').rate_to_thb
        usd_rate = CurrencyRate.objects.get(currency_code='USD').rate_to_thb

        # ເອົາສິນຄ້າມາໃຊ້
        brake_pad = Product.objects.get(barcode='BRK001')
        oil = Product.objects.get(barcode='OIL001')
        filter_oil = Product.objects.get(barcode='FILT001')

        # ສ້າງບິນທີ 1
        if not Order.objects.filter(invoice_no='INV-2024-001').exists():
            order1 = Order.objects.create(
                invoice_no='INV-2024-001',
                customer_name='ທ່ານ ສົມຊາຍ ພົມມະວົງ',
                customer_phone='020 5555 1111',
                car_register_no='ນທ 1234',
                car_province='ນະຄອນຫຼວງວຽງຈັນ',
                car_brand='Toyota',
                car_model='Vios',
                car_frame_no='ABC123456',
                car_mileage='50000',
                car_colour='ສີເທົາ',
                mechanic_name='ຊ່າງບຸນມີ',
                sale_representative='ນາງສິດາ',
                subtotal_thb=Decimal('1210.00'),  # 650 + 380 + 180
                discount_thb=Decimal('50.00'),
                tax_percent=Decimal('7.00'),
                tax_amount_thb=Decimal('81.20'),  # (1210-50) * 0.07
                net_amount_thb=Decimal('1241.20'),  # 1210 - 50 + 81.20
                rate_lak=lak_rate,
                rate_usd=usd_rate,
                net_amount_lak=Decimal('1241.20') * lak_rate,
                net_amount_usd=Decimal('1241.20') * usd_rate,
                remarks='ບິນຕົວຢ່າງທີ 1',
                user=user
            )

            # ເພີ່ມລາຍການສິນຄ້າ
            OrderItem.objects.create(
                order=order1,
                product=brake_pad,
                description=brake_pad.name,
                quantity=1,
                unit_price_thb=brake_pad.sell_price,
                discount_percent=Decimal('0.00'),
                discount_amount_thb=Decimal('0.00'),
                total_amount_thb=brake_pad.sell_price
            )

            OrderItem.objects.create(
                order=order1,
                product=oil,
                description=oil.name,
                quantity=1,
                unit_price_thb=oil.sell_price,
                discount_percent=Decimal('0.00'),
                discount_amount_thb=Decimal('0.00'),
                total_amount_thb=oil.sell_price
            )

            OrderItem.objects.create(
                order=order1,
                product=filter_oil,
                description=filter_oil.name,
                quantity=1,
                unit_price_thb=filter_oil.sell_price,
                discount_percent=Decimal('0.00'),
                discount_amount_thb=Decimal('0.00'),
                total_amount_thb=filter_oil.sell_price
            )

            self.stdout.write(self.style.SUCCESS(f'  ✓ ສ້າງບິນ {order1.invoice_no}'))
        else:
            self.stdout.write('  - ບິນ INV-2024-001 ມີຢູ່ແລ້ວ')

        # ສ້າງບິນທີ 2
        tire = Product.objects.get(barcode='TIRE001')
        battery = Product.objects.get(barcode='BAT001')

        if not Order.objects.filter(invoice_no='INV-2024-002').exists():
            order2 = Order.objects.create(
                invoice_no='INV-2024-002',
                customer_name='ທ່ານ ໝາຍວັນ ແສງສຸລິ',
                customer_phone='020 9999 2222',
                car_register_no='ນທ 5678',
                car_province='ນະຄອນຫຼວງວຽງຈັນ',
                car_brand='Honda',
                car_model='City',
                car_frame_no='XYZ789012',
                car_mileage='35000',
                car_colour='ສີຂາວ',
                mechanic_name='ຊ່າງວັນໄຊ',
                sale_representative='ທ່ານປອງ',
                subtotal_thb=Decimal('10650.00'),  # (2200*4) + 1850
                discount_thb=Decimal('650.00'),
                tax_percent=Decimal('7.00'),
                tax_amount_thb=Decimal('700.00'),
                net_amount_thb=Decimal('10700.00'),
                rate_lak=lak_rate,
                rate_usd=usd_rate,
                net_amount_lak=Decimal('10700.00') * lak_rate,
                net_amount_usd=Decimal('10700.00') * usd_rate,
                remarks='ບິນຕົວຢ່າງທີ 2 - ປ່ຽນຢາງ 4 ເສັ້ນ ແລະ ແບັດເຕີຣີ',
                user=user
            )

            # ຢາງ 4 ເສັ້ນ
            OrderItem.objects.create(
                order=order2,
                product=tire,
                description=tire.name,
                quantity=4,
                unit_price_thb=tire.sell_price,
                discount_percent=Decimal('5.00'),
                discount_amount_thb=Decimal('440.00'),  # 2200*4*0.05
                total_amount_thb=Decimal('8360.00')  # 8800 - 440
            )

            # ແບັດເຕີຣີ
            OrderItem.objects.create(
                order=order2,
                product=battery,
                description=battery.name,
                quantity=1,
                unit_price_thb=battery.sell_price,
                discount_percent=Decimal('0.00'),
                discount_amount_thb=Decimal('0.00'),
                total_amount_thb=battery.sell_price
            )

            self.stdout.write(self.style.SUCCESS(f'  ✓ ສ້າງບິນ {order2.invoice_no}'))
        else:
            self.stdout.write('  - ບິນ INV-2024-002 ມີຢູ່ແລ້ວ')
