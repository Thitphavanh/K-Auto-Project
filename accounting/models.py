from django.db import models
from django.utils import timezone
from store.models import Order  # Import Order from store app

class CashBook(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'ລາຍຮັບ (Income)'),
        ('OUT', 'ລາຍຈ່າຍ (Expense)'),
    )
    
    CURRENCY_CHOICES = (
        ('LAK', 'LAK - ກີບ (₭)'),
        ('THB', 'THB - ບາດ (฿)'),
        ('USD', 'USD - ໂດລາ ($)'),
    )
    
    date = models.DateField(default=timezone.now, verbose_name="ວັນທີ")
    time = models.TimeField(default=timezone.now, verbose_name="ເວລາ")
    description = models.CharField(max_length=255, verbose_name="ລາຍການ")
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES, verbose_name="ປະເພດ")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='LAK', verbose_name="ສະກຸນເງິນ")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="ຈຳນວນເງິນ")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="ໝວດໝູ່", help_text="ຕົວຢ່າງ: ຄ່າອາຫານ, ຄ່າຂົນສົ່ງ, ຂາຍສິນຄ້າ ໜ້າຮ້ານ")
    
    # Optional relation to Order (from store app)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ບິນອ້າງອີງ")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ບັນຊີລາຍຮັບ-ລາຍຈ່າຍ"
        verbose_name_plural = "ບັນຊີລາຍຮັບ-ລາຍຈ່າຍ"
        ordering = ['-date', '-time', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.description} ({self.get_transaction_type_display()} {self.amount:,.0f})"
