from django.contrib import admin
from .models import Product, Transaction, Brand, Category, Order, OrderItem, CurrencyRate, Customer


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


# ProductAdmin ແລະ TransactionAdmin ອັນເດີມ...


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # ສະແດງຄໍລຳຫຍັງແດ່ໃນຕາຕະລາງ
    list_display = ("barcode", "name", "category", "brand", "quantity", "cost_price", "sell_price")

    # ເພີ່ມຊ່ອງຄົ້ນຫາ (ສາມາດເອົາເືຄື່ອງຍິງບາໂຄດ ຍິງໃສ່ຊ່ອງ Search ໄດ້ເລີຍ)
    search_fields = ("barcode", "name")

    # ຕົວ​ກອງ​ຂໍ້​ມູນ
    list_filter = ("category", "brand", "quantity")

    # ຈັດລຽງຕາມຈຳນວນນ້ອຍໄປຫາຫຼາຍ (ເພື່ອເບິ່ງຂອງໃກ້ໝົດ)
    ordering = ("quantity",)

    # Auto-generate slug from name in Admin
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "transaction_type",
        "product",
        "amount",
        "total_value",
        "user",
    )
    list_filter = ("transaction_type", "created_at", "user")
    search_fields = ("product__name", "product__barcode")

    # ຫ້າມແກ້ໄຂປະຫວັດ (ເພື່ອຄວາມໂປ່ງໃສ) - Optional
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    list_display = ("currency_code", "name", "rate_to_thb", "symbol")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("invoice_no", "customer_name", "net_amount_thb", "created_at")
    inlines = [OrderItemInline]
    search_fields = ("invoice_no", "customer_name")
    list_filter = ("created_at",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "phone", "car_brand", "car_model", "car_register_no")
    search_fields = ("code", "name", "phone", "car_register_no")
    list_filter = ("car_brand", "created_at")
