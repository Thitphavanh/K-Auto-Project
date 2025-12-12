from django import forms

class RestockForm(forms.Form):
    barcode = forms.CharField(
        label='สแกนบาร์โค้ด',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'ยิงบาร์โค้ดที่นี่...',
            'autofocus': 'autofocus',  # สำคัญ! ให้ Cursor มารอที่นี่ทันที
            'autocomplete': 'off'      # ปิด Auto-complete ไม่ให้บังจอ
        })
    )