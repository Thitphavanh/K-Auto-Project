from django.contrib import admin
from .models import CashBook

@admin.register(CashBook)
class CashBookAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'description', 'category', 'transaction_type_colored', 'amount_formatted', 'currency', 'created_at')
    list_filter = ('transaction_type', 'date', 'category')
    search_fields = ('description', 'category', 'amount')
    date_hierarchy = 'date'
    ordering = ('-date', '-time')
    
    def transaction_type_colored(self, obj):
        from django.utils.html import format_html
        if obj.transaction_type == 'IN':
            color = 'green'
            label = 'ລາຍຮັບ (Income)'
        else:
            color = 'red'
            label = 'ລາຍຈ່າຍ (Expense)'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)
    transaction_type_colored.short_description = 'ປະເພດ'

    def amount_formatted(self, obj):
        return f"{obj.amount:,.0f} ₭"
    amount_formatted.short_description = 'ຈຳນວນເງິນ'
