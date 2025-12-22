from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


# 1. ສ້າງ Model ສຳລັບ Brand ໃໝ່
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="ຊື່ຍີ່ຫໍ້")
    image = models.ImageField(
        upload_to="brands/", blank=True, null=True, verbose_name="ໂລໂກ້"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ຍີ່ຫໍ້"
        verbose_name_plural = "ຂໍ້ມູນຍີ່ຫໍ້ທັງໝົດ"


class Customer(models.Model):
    # Customer Code (Unique ID for reference)
    code = models.CharField(max_length=20, unique=True, verbose_name="ລະຫັດລູກຄ້າ")
    
    name = models.CharField(max_length=200, verbose_name="ຊື່ລູກຄ້າ")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="ເບີໂທ")
    
    # Default Vehicle Info (Latest one used)
    car_register_no = models.CharField(max_length=50, blank=True, null=True, verbose_name="ທະບຽນລົດ")
    car_province = models.CharField(max_length=100, blank=True, null=True, verbose_name="ແຂວງ")
    car_brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="ຍີ່ຫໍ້ລົດ")
    car_model = models.CharField(max_length=100, blank=True, null=True, verbose_name="ລຸ້ນ")
    car_frame_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="ເລກຖັງ")
    car_color = models.CharField(max_length=50, blank=True, null=True, verbose_name="ສີ")
    car_mileage = models.IntegerField(default=0, verbose_name="ເລກກິໂລ (km)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate Customer Code: A-000001
            last_cust = Customer.objects.order_by("-id").first()
            if last_cust:
                try:
                    last_id = int(last_cust.code.split("-")[-1])
                    new_id = last_id + 1
                except ValueError:
                    new_id = last_cust.id + 1
            else:
                new_id = 1
            self.code = f"A-{str(new_id).zfill(6)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "ຂໍ້ມູນລູກຄ້າ"
        verbose_name_plural = "ຂໍ້ມູນລູກຄ້າທັງໝົດ"


class Product(models.Model):
    # Barcode ຄວນເປັນ unique (ຫ້າມຊ້ຳກັນ)
    barcode = models.CharField(max_length=50, unique=True, verbose_name="ລະຫັດບາໂຄດ")
    name = models.CharField(max_length=200, verbose_name="ຊື່ອາໄຫຼ່")
    slug = models.SlugField(
        max_length=250, unique=True, blank=True, verbose_name="URL Slug"
    )
    description = models.TextField(blank=True, null=True, verbose_name="ລາຍລະອຽດ")

    # ຮູບພາບສິນຄ້າ
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name="ຮູບພາບ"
    )

    # ໝວດໝູ່ສິນຄ້າ
    category = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="ໝວດໝູ່"
    )

    # 2. ແກ້ໄຂບ່ອນນີ້: ປ່ຽນຈາກ CharField ເປັນ ForeignKey
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ຍີ່ຫໍ້"
    )
    # ໃຊ້ DecimalField ສຳລັບເງິນ ເພື່ອຄວາມຖືກຕ້ອງກວ່າ Float
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="ຕົ້ນທຶນ"
    )
    sell_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="ລາຄາຂາຍ"
    )

    quantity = models.IntegerField(default=0, verbose_name="ຈຳນວນຄົງເຫຼືອ")

    def save(self, *args, **kwargs):
        # ສ້າງ slug ອັດຕະໂນມັດຖ້າຍັງບໍ່ມີ
        if not self.slug:
            # ໃຊ້ barcode ເປັນ base ສຳລັບ slug ເພາະມັນ unique
            base_slug = slugify(self.barcode)
            self.slug = base_slug

            # ກວດສອບວ່າ slug ນີ້ມີຢູ່ແລ້ວບໍ່, ຖ້າມີກໍເພີ່ມເລກທ້າຍ
            counter = 1
            while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.barcode})"

    class Meta:
        verbose_name = "ສິນຄ້າ"
        verbose_name_plural = "ຂໍ້ມູນສິນຄ້າທັງໝົດ"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("IN", "ນຳເຂົ້າ (ຊື້)"),
        ("OUT", "ຂາຍອອກ"),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="ສິນຄ້າ")
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name="ຜູ້ເຮັດລາຍການ"
    )
    transaction_type = models.CharField(
        max_length=3, choices=TRANSACTION_TYPES, verbose_name="ປະເພດ"
    )
    amount = models.IntegerField(verbose_name="ຈຳນວນ")

    # ບັນທຶກລາຄາ ທີ່ເກີດຂຶ້ນຕອນນັ້ນໆ (ເຜື່ອອະນາຄົດສິນຄ້າມີການປ່ຽນລາຄາ ປະຫວັດເກົ່າຈະໄດ້ບໍ່ພ້ຽນ)
    total_value = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="ມູນຄ່າລວມ"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ວັນເວລາ")

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.amount})"

    class Meta:
        verbose_name = "ປະຫວັດການເຄື່ອນໄຫວ"
        verbose_name_plural = "ປະຫວັດການເຄື່ອນໄຫວ"

class CurrencyRate(models.Model):
    currency_code = models.CharField(max_length=3, unique=True, verbose_name="ລະຫັດສະກຸນເງິນ")  # LAK, THB, USD
    name = models.CharField(max_length=50, verbose_name="ຊື່ສະກຸນເງິນ")
    rate_to_thb = models.DecimalField(
        max_digits=15, decimal_places=6, default=1.0, verbose_name="ອັດຕາແລກປ່ຽນທຽບກັບ THB"
    )
    symbol = models.CharField(max_length=5, verbose_name="ສັນຍາລັກ")

    def __str__(self):
        return f"{self.currency_code} ({self.rate_to_thb})"

    class Meta:
        verbose_name = "ອັດຕາແລກປ່ຽນ"
        verbose_name_plural = "ຈັດການອັດຕາແລກປ່ຽນ"


class Order(models.Model):
    """ແບບຟອມບິນ K-AUTO LAO SERVICE"""
    
    # ຂໍ້ມູນບິນພື້ນຖານ
    invoice_no = models.CharField(max_length=50, unique=True, verbose_name="ເລກທີບິນ")
    date = models.DateField(default=timezone.now, verbose_name="ວັນທີ")
    
    # ຂໍ້ມູນລູກຄ້າ
    customer_name = models.CharField(max_length=200, verbose_name="ຊື່ລູກຄ້າ", blank=True, null=True)
    customer_phone = models.CharField(max_length=50, verbose_name="ເບີໂທລະສັບລູກຄ້າ", blank=True, null=True)
    customer_code = models.CharField(max_length=50, verbose_name="ລະຫັດລູກຄ້າ", blank=True, null=True)
    
    # Link to unique Customer record (Existing relationship preserved)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ລູກຄ້າ")
    
    # ຂໍ້ມູນລົດ
    car_register_no = models.CharField(max_length=100, verbose_name="ທະບຽນລົດ", blank=True, null=True)
    car_province = models.CharField(max_length=100, verbose_name="ແຂວງ", blank=True, null=True)
    car_brand = models.CharField(max_length=100, verbose_name="ຍີ່ຫໍ້ລົດ", blank=True, null=True)
    car_model = models.CharField(max_length=100, verbose_name="ແບບລົດ", blank=True, null=True)
    car_frame_no = models.CharField(max_length=100, verbose_name="ເລກຊາສີ", blank=True, null=True)
    car_color = models.CharField(max_length=50, verbose_name="ສີລົດ", blank=True, null=True)
    car_mileage = models.CharField(max_length=50, verbose_name="ເລກ km", blank=True, null=True)
    
    # ຂໍ້ມູນພະນັກງານ
    mechanic_name = models.CharField(max_length=100, verbose_name="ຊ່າງສ້ອມ", blank=True, null=True)
    sale_representative = models.CharField(max_length=100, verbose_name="ພະນັກງານຂາຍ", blank=True, null=True)
    
    # ຂໍ້ມູນການຈ່າຍເງິນ
    received_by = models.CharField(max_length=100, verbose_name="ຜູ້ຮັບເງິນ", blank=True, null=True)
    check_no = models.CharField(max_length=100, verbose_name="ເລກທີເຊັກ", blank=True, null=True)
    check_date = models.DateField(null=True, blank=True, verbose_name="ວັນທີໃນເຊັກ")
    bank_name = models.CharField(max_length=100, verbose_name="ທະນາຄານ", blank=True, null=True)
    bank_branch = models.CharField(max_length=100, verbose_name="ສາຂາ", blank=True, null=True)
    
    # ວິທີການຈ່າຍເງິນ (NEW Booleans)
    payment_cash = models.BooleanField(default=False, verbose_name="ເງິນສົດ")
    payment_check = models.BooleanField(default=False, verbose_name="ເຊັກທະນາຄານ")
    payment_credit = models.BooleanField(default=False, verbose_name="ເຄຣດິດ/ຕິດໜີ້")
    
    # ຈຳນວນເງິນຕາມວິທີການຈ່າຍ
    payment_amount_cash = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຈຳນວນເງິນສົດ")
    payment_amount_check = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຈຳນວນເງິນເຊັກ")
    payment_amount_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຈຳນວນເງິນເຄຣດິດ")
    
    # ຍອດລວມ (Subtotal) ໃນສະກຸນເງິນຕ່າງໆ
    subtotal_lak = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຍອດລວມ (LAK)")
    subtotal_thb = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຍອດລວມ (THB)")
    subtotal_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຍອດລວມ (USD)")
    
    # ສ່ວນຫຼຸດລວມ (Total Discount)
    discount_lak = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ສ່ວນຫຼຸດລວມ (LAK)")
    discount_thb = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ສ່ວນຫຼຸດລວມ (THB)")
    discount_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ສ່ວນຫຼຸດລວມ (USD)")
    
    # ອາກອນ (Tax)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="ອາກອນ %")
    tax_amount_lak = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຈຳນວນອາກອນ (LAK)")
    tax_amount_thb = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຈຳນວນອາກອນ (THB)")
    tax_amount_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຈຳນວນອາກອນ (USD)")
    
    # ລວມສຸດທິ (Net Total)
    net_amount_lak = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ລວມສຸດທິ (LAK)")
    net_amount_thb = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ລວມສຸດທິ (THB)")
    net_amount_usd = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ລວມສຸດທິ (USD)")
    
    # Exchange snaphost kept for reference
    rate_lak = models.DecimalField(max_digits=15, decimal_places=6, default=1)
    rate_usd = models.DecimalField(max_digits=15, decimal_places=6, default=1)

    # ຂໍ້ມູນລາຍເຊັນ
    received_by_date = models.DateField(null=True, blank=True, verbose_name="ວັນທີຜູ້ຮັບເງິນ")
    paid_by = models.CharField(max_length=100, verbose_name="ຜູ້ຈ່າຍເງິນ", blank=True, null=True)
    paid_by_date = models.DateField(null=True, blank=True, verbose_name="ວັນທີຜູ້ຈ່າຍເງິນ")
    good_received_by = models.CharField(max_length=100, verbose_name="ຜູ້ຮັບສິນຄ້າ", blank=True, null=True)
    good_received_by_date = models.DateField(null=True, blank=True, verbose_name="ວັນທີຜູ້ຮັບສິນຄ້າ")
    
    # System Info
    remarks = models.TextField(blank=True, null=True, verbose_name="ໝາຍເຫດ")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="ຜູ້ຂາຍ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ສ້າງເມື່ອ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="ອັບເດດເມື່ອ")
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "ບິນ"
        verbose_name_plural = "ບິນທັງໝົດ"
    
    def __str__(self):
        return f"{self.invoice_no} - {self.customer_name}"
    
    def calculate_totals(self):
        """ຄິດໄລ່ຍອດລວມທັງໝົດ"""
        items = self.items.all()
        
        # ຄິດໄລ່ຍອດລວມ (Subtotal)
        self.subtotal_thb = sum(item.amount for item in items)
        
        # ຄິດໄລ່ສ່ວນຫຼຸດລວມ
        self.discount_thb = sum(item.discount_amount for item in items)
        
        # ຄິດໄລ່ອາກອນ
        subtotal_after_discount = self.subtotal_thb - self.discount_thb
        self.tax_amount_thb = (subtotal_after_discount * self.tax_percent) / 100
        
        # ຄິດໄລ່ລວມສຸດທິ
        self.net_amount_thb = subtotal_after_discount + self.tax_amount_thb
        
        # ແປງເປັນສະກຸນເງິນອື່ນໆ ໂດຍໃຊ້ CurrencyRate model ຖ້າມີ
        from .models import CurrencyRate
        rates = {r.currency_code: r.rate_to_thb for r in CurrencyRate.objects.all()}
        
        thb_to_lak = rates.get('LAK', Decimal('1'))
        thb_to_usd = rates.get('USD', Decimal('1'))
        
        # User snippet used hardcoded values, but let's use the actual rates for accuracy
        # or fall back to their snippet values if rates don't exist.
        
        self.subtotal_lak = self.subtotal_thb * thb_to_lak
        self.subtotal_usd = self.subtotal_thb * thb_to_usd
        
        self.discount_lak = self.discount_thb * thb_to_lak
        self.discount_usd = self.discount_thb * thb_to_usd
        
        self.tax_amount_lak = self.tax_amount_thb * thb_to_lak
        self.tax_amount_usd = self.tax_amount_thb * thb_to_usd
        
        self.net_amount_lak = self.net_amount_thb * thb_to_lak
        self.net_amount_usd = self.net_amount_thb * thb_to_usd
        
        self.save()
    
    def generate_invoice_no(self):
        """ສ້າງເລກທີບິນອັດຕະໂນມັດ"""
        if not self.invoice_no:
            year = self.date.strftime('%y')
            month_day = self.date.strftime('%m%d')
            # Check for current year invoice format IVCYMMDD-XXXXX
            last_order = Order.objects.filter(
                invoice_no__startswith=f'IVC{year}{month_day}-'
            ).order_by('-invoice_no').first()
            
            if last_order:
                try:
                    last_number = int(last_order.invoice_no.split('-')[1])
                except (IndexError, ValueError):
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.invoice_no = f'IVC{year}{month_day}-{str(new_number).zfill(5)}'
    
    def save(self, *args, **kwargs):
        if not self.invoice_no:
            self.generate_invoice_no()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """ລາຍການສິນຄ້າໃນບິນ"""
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="ບິນ"
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    item_no = models.IntegerField(verbose_name="ລຳດັບ", default=1)
    ref_code = models.CharField(max_length=100, verbose_name="ລະຫັດສິນຄ້າ", blank=True, null=True)
    description = models.TextField(verbose_name="ລາຍການ")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="ຈຳນວນ")
    unit = models.CharField(max_length=50, default="ອັນ", verbose_name="ໜ່ວຍ")
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ລາຄາຕໍ່ໜ່ວຍ")
    
    # ສ່ວນຫຼຸດ
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="ສ່ວນຫຼຸດ %")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຈຳນວນສ່ວນຫຼຸດ")
    
    # ລວມ
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ຈຳນວນເງິນລວມ")
    
    # ຂໍ້ມູນລະບົບ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ສ້າງເມື່ອ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="ອັບເດດເມື່ອ")
    
    class Meta:
        ordering = ['item_no']
        verbose_name = "ລາຍການສິນຄ້າ"
        verbose_name_plural = "ລາຍການສິນຄ້າທັງໝົດ"
    
    def __str__(self):
        return f"{self.item_no}. {self.description}"
    
    def calculate_amount(self):
        """ຄິດໄລ່ຈຳນວນເງິນລວມ"""
        subtotal = self.quantity * self.unit_price
        
        # ຄິດໄລ່ສ່ວນຫຼຸດ
        if self.discount_percent > 0:
            self.discount_amount = (subtotal * self.discount_percent) / 100
        
        # ຈຳນວນເງິນລວມຫຼັງຫັກສ່ວນຫຼຸດ
        self.amount = subtotal - self.discount_amount
        
        return self.amount
    
    def save(self, *args, **kwargs):
        self.calculate_amount()
        super().save(*args, **kwargs)
        # ອັບເດດຍອດລວມຂອງບິນ
        self.order.calculate_totals()
