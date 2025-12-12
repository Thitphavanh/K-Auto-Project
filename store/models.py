from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


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
