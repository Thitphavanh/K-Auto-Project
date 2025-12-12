from django.contrib import admin
from .models import Product, Transaction, Brand  # <--- import Brand ເພີ່ມ


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


# ProductAdmin ແລະ TransactionAdmin ອັນເດີມ...


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # ສະແດງຄໍລຳຫຍັງແດ່ໃນຕາຕະລາງ
    list_display = ("barcode", "name", "quantity", "cost_price", "sell_price")

    # ເພີ່ມຊ່ອງຄົ້ນຫາ (ສາມາດເອົາເືຄື່ອງຍິງບາໂຄດ ຍິງໃສ່ຊ່ອງ Search ໄດ້ເລີຍ)
    search_fields = ("barcode", "name")

    # ຕົວ​ກອງ​ຂໍ້​ມູນ
    list_filter = ("quantity",)

    # ຈັດລຽງຕາມຈຳນວນນ້ອຍໄປຫາຫຼາຍ (ເພື່ອເບິ່ງຂອງໃກ້ໝົດ)
    ordering = ("quantity",)


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
