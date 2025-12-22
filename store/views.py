from .models import Product, Transaction, Brand, Order, OrderItem, CurrencyRate, Customer, Category
from django.db import transaction as db_transaction
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)  # <--- import ເພີ່ມ
from django.contrib import messages  # Import messages for notifications
from django.db.models import Sum, Count, Q  # <--- ໃຊ້ລວມຜົນ ແລະ ນັບຈຳນວນ
from django.utils import timezone
from datetime import timedelta
from .forms import RestockForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime


# Home page view
def home_view(request):
    """ໜ້າຫຼັກ (Home Page)"""
    # ດຶງສິນຄ້າທັງໝົດ (ຫຼືສິນຄ້າລ່າສຸດ 8 ຊິ້ນ)
    # ເພີ່ມ select_related('brand')
    products = Product.objects.select_related("brand").all().order_by("-id")[:8]
    context = {"products": products}
    return render(request, "index.html", context)


def product_list_view(request):
    """ໜ້າລາຍການສິນຄ້າທັງໝົດ"""
    # ດຶງສິນຄ້າທັງໝົດ
    products = Product.objects.select_related("brand").all()

    # ການຄົ້ນຫາ (Search)
    search_query = request.GET.get("search", "")
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(barcode__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    # ການກັ່ນຕອງຕາມໝວດໝູ່ (Category Filter)
    category_filter = request.GET.get("category", "")
    if category_filter:
        products = products.filter(category=category_filter)

    # ການກັ່ນຕອງຕາມຍີ່ຫໍ້ (Brand Filter)
    brand_filter = request.GET.get("brand", "")
    if brand_filter:
        products = products.filter(brand__id=brand_filter)

    # ການຈັດລຽງ (Sorting)
    sort_by = request.GET.get("sort", "-id")  # default: ລ່າສຸດກ່ອນ
    if sort_by:
        products = products.order_by(sort_by)

    # ດຶງລາຍການໝວດໝູ່ທັງໝົດ (ສຳລັບ dropdown filter)
    categories = Category.objects.all().order_by("name")

    # ດຶງລາຍການຍີ່ຫໍ້ທັງໝົດ (ສຳລັບ dropdown filter)
    brands = Brand.objects.all().order_by("name")

    # Pagination (ສະແດງ 12 ລາຍການຕໍ່ໜ້າ)
    paginator = Paginator(products, 12)
    page = request.GET.get("page", 1)

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    context = {
        "products": products_page,
        "search_query": search_query,
        "category_filter": category_filter,
        "brand_filter": brand_filter,
        "sort_by": sort_by,
        "categories": categories,
        "brands": brands,
        "total_products": paginator.count,
    }

    return render(request, "store/product-list.html", context)


def product_detail_view(request, slug):
    """ໜ້າລາຍລະອຽດສິນຄ້າ"""
    try:
        # ເພີ່ມ select_related('brand')
        product = Product.objects.select_related("brand").get(slug=slug)
        context = {"product": product}
        return render(request, "store/product-detail.html", context)
    except Product.DoesNotExist:
        messages.error(request, "ບໍ່ພົບສິນຄ້ານີ້ໃນລະບົບ")
        return redirect("home")


# ຟັງຊັນກວດສອບວ່າເປັນ "Superuser" ຫຼືບໍ່?
def is_admin(user):
    return user.is_superuser


@login_required
def stock_in_view(request):
    last_scanned_item = None  # เอาไว้โชว์ว่าเพิ่งยิงตัวไหนไป

    if request.method == "POST":
        form = RestockForm(request.POST)
        if form.is_valid():
            barcode_input = form.cleaned_data["barcode"]

            try:
                # ค้นหาอะไหล่จากบาร์โค้ด
                part = Product.objects.get(barcode=barcode_input)

                # เพิ่มจำนวนสต็อก +1
                part.quantity += 1
                part.save()

                last_scanned_item = part
                messages.success(
                    request, f"✅ รับเข้าสำเร็จ: {part.name} (รวม: {part.quantity})"
                )

            except Product.DoesNotExist:
                messages.error(request, f"❌ ไม่พบสินค้ารหัส: {barcode_input}")
                # ตรงนี้อาจจะ Redirect ไปหน้าเพิ่มสินค้าใหม่ก็ได้ถ้าต้องการ

            return redirect("stock-in")  # Redirect กลับมาหน้าเดิมเพื่อเคลียร์ค่าในฟอร์ม

    else:
        form = RestockForm()

    context = {"form": form, "last_item": last_scanned_item}
    return render(request, "store/stock-in.html", context)


@login_required  # ຕ້ອງ Login ກ່ອນຈຶ່ງຈະໃຊ້ໜ້ານີ້ໄດ້
def pos_view(request):
    if request.method == "POST":
        barcode = request.POST.get("barcode")  # ຮັບຄ່າຈາກເຄື່ອງຍິງບາໂຄດ

        try:
            # 1. ຄົ້ນຫាសິນຄ້າຕາມບາໂຄດ
            product = Product.objects.get(barcode=barcode)

            # 2. ກວດສອບວ່າສິນຄ້າໝົດຫຼືບໍ່?
            if product.quantity > 0:
                # 3. ຕັດສະຕັອກ
                product.quantity -= 1
                product.save()

                # 4. ບັນທຶກ Transaction (ລາຍຮັບ)
                Transaction.objects.create(
                    product=product,
                    user=request.user,
                    transaction_type="OUT",
                    amount=1,
                    total_value=product.sell_price,
                )

                # ສົ່ງຂໍ້ຄວາມແຈ້ງເຕືອນສີຂຽວ
                messages.success(
                    request,
                    f"ຂາຍ {product.name} ສຳເລັດ! ລາຄາ: {product.sell_price:,.0f} ກີບ",
                )
            else:
                # ສິນຄ້າໝົດ
                messages.error(request, f"ສິນຄ້າ {product.name} ໝົດສະຕັອກ!")

        except Product.DoesNotExist:
            # ບໍ່ພົບລະຫັດບາໂຄດນີ້
            messages.error(request, "ບໍ່ພົບສິນຄ້ານີ້ໃນລະບົບ! ກະລຸນາກວດສອບບາໂຄດ.")

        return redirect("pos")  # ໂຫຼດໜ້າເກົ່າຄືນ ເພື່ອລໍຖ້າຍິງຄັ້ງຕໍ່ໄປ

    return render(request, "store/pos.html")


@login_required
@user_passes_test(is_admin, login_url="/pos/")
def dashboard_view(request):
    # 1. ດຶງວັນທີປະຈຸບັນ
    today = timezone.now().date()

    # 2. ຄິດໄລ່ຍອດຂາຍວັນນີ້ (ສະເພາະຂາອອກ 'OUT')
    daily_sales = (
        Transaction.objects.filter(
            transaction_type="OUT", created_at__date=today
        ).aggregate(Sum("total_value"))["total_value__sum"]
        or 0
    )

    # 3. ນັບຈຳນວນບິນວັນນີ້
    daily_orders = Transaction.objects.filter(
        transaction_type="OUT", created_at__date=today
    ).count()

    # 4. ດຶງຂໍ້ມູນ 5 ລາຍການລ່າສຸດມາສະແດງ
    recent_transactions = Transaction.objects.all().order_by("-created_at")[:5]

    # 5. ກຽມຂໍ້ມູນກຣາຟ (ຍອດຂາຍ 7 ມື້ຍ້ອນຫຼັງ)
    dates = []
    sales_data = []

    for i in range(6, -1, -1):  # ວົນລູບຍ້ອນຫຼັງ 7 ມື້
        date = today - timedelta(days=i)
        # ຄິດໄລ່ຍອດຂາຍຂອງມື້ນັ້ນ
        sales = (
            Transaction.objects.filter(
                transaction_type="OUT", created_at__date=date
            ).aggregate(Sum("total_value"))["total_value__sum"]
            or 0
        )

        dates.append(date.strftime("%d/%m"))  # ເກັບວັນທີ ເຊັ່ນ "20/11"
        sales_data.append(int(sales))  # ເກັບຍອດເງິນ

    context = {
        "daily_sales": daily_sales,
        "daily_orders": daily_orders,
        "recent_transactions": recent_transactions,
        "dates": dates,  # ສົ່ງໄປເຮັດແກນ X ຂອງກຣາຟ
        "sales_data": sales_data,  # ສົ່ງໄປເຮັດແກນ Y ຂອງກຣາຟ
    }

    return render(request, "store/dashboard.html", context)


# --- 1. API ສຳລັບດຶງຂໍ້ມູນສິນຄ້າ (ໃຊ້ Ajax ຍິງມາຖາມ) ---
@login_required
def api_get_product(request):
    barcode = request.GET.get("barcode")  # ຮັບຄ່າ barcode ຈາກ URL

    try:
        # ຄົ້ນຫາສິນຄ້າໃນຖານຂໍ້ມູນ
        product = Product.objects.get(barcode=barcode)

        # ສົ່ງຂໍ້ມູນກັບໄປເປັນ JSON
        return JsonResponse(
            {
                "found": True,
                "id": product.id,
                "name": product.name,
                "price": float(product.sell_price),  # ແປງ Decimal ເປັນ Float
                "stock": product.quantity,
                # ກວດສອບວ່າມີຮູບບໍ່ ຖ້າບໍ່ມີໃຫ້ສົ່ງຄ່າ null
                "image": product.image.url if product.image else None,
            }
        )
    except Product.DoesNotExist:
        # ຖ້າຫາບໍ່ເຫັນ
        return JsonResponse({"found": False})


# --- 2. API ສຳລັບບັນທຶກການຂາຍ (Checkout) ---

@login_required
def api_search_customer(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})
        
    customers = Customer.objects.filter(
        Q(name__icontains=query) | Q(phone__icontains=query) | Q(code__icontains=query)
    )[:10]  # Limit to 10 results
    
    results = []
    for c in customers:
        results.append({
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "phone": c.phone,
            "car_register_no": c.car_register_no,
            "car_province": c.car_province,
            "car_brand": c.car_brand,
            "car_model": c.car_model,
            "car_frame_no": c.car_frame_no,
            "car_color": c.car_color,
            "car_mileage": c.car_mileage,
            "display": f"{c.name} - {c.phone}"
        })
        
    return JsonResponse({"results": results})


@login_required
def api_search_product(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})
        
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(barcode__icontains=query)
    )[:10]
    
    results = []
    for p in products:
        results.append({
            "id": p.id,
            "name": p.name,
            "barcode": p.barcode,
            "price": float(p.sell_price),
            "unit": "ອັນ", # Default
        })
        
    return JsonResponse({"results": results})


@login_required
@csrf_exempt
def api_checkout(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cart_items = data.get("items", [])
            customer_info = data.get("customer", {})
            car_info = data.get("car", {})
            mechanic_info = data.get("mechanic", {})
            
            if not cart_items:
                return JsonResponse({"success": False, "error": "ກະຕ່າສິນຄ້າວ່າງເປົ່າ"})

            with db_transaction.atomic():
                # 1. Handle Customer (Find or Create/Update)
                customer = None
                cust_name = customer_info.get('name')
                cust_phone = customer_info.get('phone')
                cust_code = customer_info.get('code') # If exists
                
                if cust_name:
                    # Logic to find/update
                    defaults = {
                        "phone": cust_phone,
                        "car_register_no": car_info.get('register_no'),
                        "car_province": car_info.get('province'),
                        "car_brand": car_info.get('brand'),
                        "car_model": car_info.get('model'),
                        "car_frame_no": car_info.get('frame_no'),
                        "car_color": car_info.get('color'),
                        "mechanic_name": mechanic_info.get('mechanic'),
                        "sale_representative": mechanic_info.get('sale_rep'),
                    }
                    
                    if cust_code:
                         customer, created = Customer.objects.update_or_create(
                            code=cust_code,
                            defaults=defaults
                        )
                         # Also update name if changed? Maybe keep name synced.
                         customer.name = cust_name
                         customer.save()
                    else:
                        customer, created = Customer.objects.update_or_create(
                            name=cust_name,
                            defaults=defaults
                        )

                # 2. ດຶງອັດຕາແລກປ່ຽນ
                rates = {r.currency_code: r for r in CurrencyRate.objects.all()}
                rate_lak = rates.get('LAK').rate_to_thb if 'LAK' in rates else Decimal('1')
                rate_usd = rates.get('USD').rate_to_thb if 'USD' in rates else Decimal('1')

                # 3. ສ້າງ Order
                order = Order.objects.create(
                    customer=customer,
                    customer_name=cust_name, # Snapshot
                    customer_phone=cust_phone,
                    customer_code=cust_code,
                    car_register_no=car_info.get('register_no'),
                    car_province=car_info.get('province'),
                    car_brand=car_info.get('brand'),
                    car_model=car_info.get('model'),
                    car_frame_no=car_info.get('frame_no'),
                    car_mileage=car_info.get('mileage'),
                    car_color=car_info.get('color'),
                    mechanic_name=mechanic_info.get('mechanic') or (customer.mechanic_name if customer else None),
                    sale_representative=mechanic_info.get('sale_rep') or (customer.sale_representative if customer else None),
                    rate_lak=rate_lak,
                    rate_usd=rate_usd,
                    payment_cash=True, # POS default to cash for now
                    user=request.user
                )

                for item in cart_items:
                    product = Product.objects.get(id=item["id"])
                    qty = int(item["qty"])
                    price = product.sell_price
                    discount_percent = item.get("discount", 0)
                    
                    if product.quantity >= qty:
                        # ຕັດສະຕັອກ
                        product.quantity -= qty
                        product.save()

                        # ຄິດໄລ່ສ່ວນຫຼຸດ ແລະ ຍອດລວມ
                        line_total = price * qty
                        discount_amount = (line_total * discount_percent) / 100
                        final_line_total = line_total - discount_amount
                        
                        # ບັນທຶກ OrderItem
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            description=product.name,
                            quantity=qty,
                            unit="ອັນ", # Default for products
                            unit_price=price,
                            discount_percent=discount_percent,
                            discount_amount=discount_amount,
                            amount=final_line_total
                        )

                        # ບັນທຶກລົງ Transaction (Legacy compatibility)
                        Transaction.objects.create(
                            product=product,
                            user=request.user,
                            transaction_type="OUT",
                            amount=qty,
                            total_value=final_line_total,
                        )
                    else:
                        raise Exception(f"ສິນຄ້າ {product.name} ໝົດ ຫຼື ບໍ່ພໍຂາຍ!")

                # Final Calculations via model method
                order.payment_amount_cash = order.net_amount_thb # POS usually full cash
                order.calculate_totals()

            return JsonResponse({
                "success": True, 
                "order_id": order.id,
                "invoice_no": order.invoice_no
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid Method"})


@login_required
def bill_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "store/bill-detail.html", {"order": order})


# --- 3. API ສຳລັບຮັບສິນຄ້າເຂົ້າ (Stock-In) แບບ Realtime ---
@login_required
@csrf_exempt
def api_stock_in(request):
    if request.method == "POST":
        try:
            # ແກະຂໍ້ມູນ JSON ທີ່ສົ່ງມາ
            data = json.loads(request.body)
            barcode_input = data.get("barcode", "").strip()

            if not barcode_input:
                return JsonResponse({"success": False, "error": "ບາໂຄດວ່າງເປົ່າ"})

            try:
                # ຄົ້ນຫາສິນຄ້າຈາກບາໂຄດ
                product = Product.objects.select_related("brand").get(
                    barcode=barcode_input
                )

                # ເກັບຈຳນວນເກົ່າກ່ອນເພີ່ມ
                old_quantity = product.quantity

                # ເພີ່ມຈຳນວນສະຕັອກ +1
                product.quantity += 1
                product.save()

                # ບັນທຶກ Transaction (ນຳເຂົ້າ)
                transaction = Transaction.objects.create(
                    product=product,
                    user=request.user,
                    transaction_type="IN",
                    amount=1,
                    total_value=product.cost_price,
                )

                # --- Send WebSocket Message ---
                channel_layer = get_channel_layer()
                product_data = {
                    "id": product.id,
                    "barcode": product.barcode,
                    "name": product.name,
                    "brand": product.brand.name if product.brand else "-",
                    "category": product.category.name if product.category else "-",
                    "image": product.image.url if product.image else None,
                    "old_quantity": old_quantity,
                    "new_quantity": product.quantity,
                    "cost_price": float(product.cost_price),
                }

                async_to_sync(channel_layer.group_send)(
                    "inventory_updates",
                    {
                        "type": "stock_added",
                        "product": product_data,
                        "timestamp": transaction.created_at.isoformat(),
                    },
                )
                # --- End WebSocket Message ---

                # ສົ່ງຂໍ້ມູນກັບໄປພ້ອມຮູບພາບ
                return JsonResponse({"success": True, "product": product_data})

            except Product.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": f"ບໍ່ພົບສິນຄ້າລະຫັດ: {barcode_input}"}
                )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid Method"})




@login_required
@csrf_exempt
def api_manual_checkout(request):
    """
    Handle Manual Bill Creation (Free-text items)
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            items = data.get("items", [])
            customer_info = data.get("customer", {})
            car_info = data.get("car", {})
            mechanic_info = data.get("mechanic", {})
            payment_info = data.get("payment", {})
            tax_percent = float(data.get("tax_percent", 0))

            with db_transaction.atomic():
                # 1. Handle Customer
                customer = None
                cust_name = customer_info.get('name')
                cust_phone = customer_info.get('phone')
                cust_code = customer_info.get('code')

                if cust_name:
                    defaults = {
                        "phone": cust_phone,
                        "car_register_no": car_info.get('register_no'),
                        "car_province": car_info.get('province'),
                        "car_brand": car_info.get('brand'),
                        "car_model": car_info.get('model'),
                        "car_frame_no": car_info.get('frame'),
                        "car_color": car_info.get('color'),
                    }
                    if cust_code:
                        customer, created = Customer.objects.update_or_create(code=cust_code, defaults=defaults)
                        if customer.name != cust_name:
                             customer.name = cust_name
                             customer.save()
                    else:
                        customer, created = Customer.objects.update_or_create(name=cust_name, defaults=defaults)

                # 2. Rates
                rates = {r.currency_code: r for r in CurrencyRate.objects.all()}
                rate_lak_val = rates.get('LAK').rate_to_thb if 'LAK' in rates else Decimal('1')
                rate_usd_val = rates.get('USD').rate_to_thb if 'USD' in rates else Decimal('1')

                # 3. Create Order
                order = Order.objects.create(
                    customer=customer,
                    customer_name=cust_name,
                    customer_phone=cust_phone,
                    customer_code=cust_code,
                    car_register_no=car_info.get('register_no'),
                    car_province=car_info.get('province'),
                    car_brand=car_info.get('brand'),
                    car_model=car_info.get('model'),
                    car_frame_no=car_info.get('frame'),
                    car_mileage=car_info.get('mileage'),
                    car_color=car_info.get('color'),
                    mechanic_name=mechanic_info.get('name'),
                    sale_representative=mechanic_info.get('rep'),
                    
                    # Payment Info
                    received_by=payment_info.get('received_by'),
                    check_no=payment_info.get('check_no'),
                    check_date=payment_info.get('check_date') if payment_info.get('check_date') else None,
                    bank_name=payment_info.get('bank_name'),
                    bank_branch=payment_info.get('bank_branch'),
                    payment_amount_cash=Decimal(str(payment_info.get('amount_cash', 0))),
                    payment_amount_check=Decimal(str(payment_info.get('amount_check', 0))),
                    payment_amount_credit=Decimal(str(payment_info.get('amount_credit', 0))),

                    # Booleans based on amounts
                    payment_cash=Decimal(str(payment_info.get('amount_cash', 0))) > 0,
                    payment_check=Decimal(str(payment_info.get('amount_check', 0))) > 0,
                    payment_credit=Decimal(str(payment_info.get('amount_credit', 0))) > 0,

                    tax_percent=Decimal(str(tax_percent)),
                    rate_lak=rate_lak_val,
                    rate_usd=rate_usd_val,
                    user=request.user
                )

                for item in items:
                    qty = Decimal(str(item.get('qty', 1)))
                    price = Decimal(str(item.get('price', 0)))
                    discount_amount = Decimal(str(item.get('discount', 0)))
                    desc = item.get('desc', 'Item')
                    ref_code = item.get('ref_code', '')

                    OrderItem.objects.create(
                        order=order,
                        product=None, # Manual item
                        ref_code=ref_code,
                        description=desc,
                        quantity=qty,
                        unit=item.get('unit', 'ອັນ'),
                        unit_price=price,
                        discount_percent=discount_amount  # Named discount in JSON but contains %
                    )

                # Final Calculations via model method
                order.calculate_totals()

            return JsonResponse({"success": True, "order_id": order.id, "invoice_no": order.invoice_no})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
            
    return JsonResponse({"success": False, "error": "Invalid Method"})


@login_required
def input_bill_view(request):
    try:
        rates = {r.currency_code: r for r in CurrencyRate.objects.all()}
        rate_lak_obj = rates.get('LAK')
        rate_usd_obj = rates.get('USD')

        rate_lak = float(rate_lak_obj.rate_to_thb) if rate_lak_obj else 0.0
        rate_usd = float(rate_usd_obj.rate_to_thb) if rate_usd_obj else 1.0
    except Exception:
        # Fallback to default rates if there's any error
        rate_lak = 0.0
        rate_usd = 1.0

    context = {
        'rate_lak': rate_lak,
        'rate_usd': rate_usd
    }
    return render(request, "store/input_customer_bill.html", context)

@login_required
def customer_registration_view(request):
    """Standalone page for Customer & Vehicle Registration"""
    return render(request, "store/customer_registration.html")

@csrf_exempt
@login_required
def api_save_customer(request):
    """API to Save/Update Customer & Vehicle details independently"""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"})
    
    try:
        data = json.loads(request.body)
        cust_id = data.get("id")
        
        # 1. Handle Customer Record
        if cust_id:
            customer = get_object_or_404(Customer, id=cust_id)
        else:
            customer = Customer()
        
        customer.name = data.get("name")
        customer.phone = data.get("phone")
        
        # Update/Set Vehicle Info
        customer.car_register_no = data.get("car_register_no")
        customer.car_province = data.get("car_province")
        customer.car_brand = data.get("car_brand")
        customer.car_model = data.get("car_model")
        customer.car_frame_no = data.get("car_frame_no")
        customer.car_color = data.get("car_color")
        customer.car_mileage = data.get("car_mileage") or 0
        
        # New Fields
        customer.mechanic_name = data.get("mechanic_name")
        customer.sale_representative = data.get("sale_representative")
        
        customer.save()
        
        return JsonResponse({
            "success": True, 
            "customer": {
                "id": customer.id,
                "code": customer.code,
                "name": customer.name,
                "phone": customer.phone,
                "car_register_no": customer.car_register_no,
                "car_brand": customer.car_brand,
                "car_model": customer.car_model,
                "car_mileage": customer.car_mileage,
                "mechanic_name": customer.mechanic_name,
                "sale_representative": customer.sale_representative
            }
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

def order_list(request):
    """ສະແດງລາຍການບິນທັງໝົດ"""
    orders = Order.objects.all().order_by('-date', '-invoice_no')
    
    # ຄົ້ນຫາ
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(invoice_no__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_code__icontains=search_query) |
            Q(car_register_no__icontains=search_query)
        )
    
    # ກັ່ນຕອງຕາມວັນທີ
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        orders = orders.filter(date__gte=date_from)
    if date_to:
        orders = orders.filter(date__lte=date_to)
    
    context = {
        'orders': orders,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'orders/order_list.html', context)


def order_detail(request, invoice_no):
    """ສະແດງລາຍລະອຽດບິນ (ແບບພິມໄດ້)"""
    order = get_object_or_404(Order, invoice_no=invoice_no)
    items = order.items.all().order_by('item_no')
    
    context = {
        'order': order,
        'items': items,
    }
    
    return render(request, 'orders/bill-detail.html', context)


def order_create(request):
    """ສ້າງບິນໃໝ່"""
    if request.method == 'POST':
        with db_transaction.atomic():
            # ສ້າງບິນໃໝ່
            order = Order(user=request.user)
            
            # ຂໍ້ມູນພື້ນຖານ
            order_date = request.POST.get('date')
            if order_date:
                order.date = order_date
            else:
                order.date = timezone.now().date()
            
            # ຂໍ້ມູນລູກຄ້າ
            order.customer_name = request.POST.get('customer_name', '')
            order.customer_phone = request.POST.get('customer_phone', '')
            order.customer_code = request.POST.get('customer_code', '')
            
            # ຂໍ້ມູນລົດ
            order.car_register_no = request.POST.get('car_register_no', '')
            order.car_province = request.POST.get('car_province', '')
            order.car_brand = request.POST.get('car_brand', '')
            order.car_model = request.POST.get('car_model', '')
            order.car_frame_no = request.POST.get('car_frame_no', '')
            order.car_color = request.POST.get('car_color', '')
            order.car_mileage = request.POST.get('car_mileage', '')
            
            # ຂໍ້ມູນພະນັກງານ
            order.mechanic_name = request.POST.get('mechanic_name', '')
            order.sale_representative = request.POST.get('sale_representative', '')
            
            # ຂໍ້ມູນການຈ່າຍເງິນ
            order.received_by = request.POST.get('received_by', '')
            order.check_no = request.POST.get('check_no', '')
            check_date = request.POST.get('check_date', '')
            if check_date:
                order.check_date = check_date
            else:
                order.check_date = None
            order.bank_name = request.POST.get('bank_name', '')
            order.bank_branch = request.POST.get('bank_branch', '')
            
            # ວິທີການຈ່າຍເງິນ
            order.payment_cash = request.POST.get('payment_cash') == 'on'
            order.payment_check = request.POST.get('payment_check') == 'on'
            order.payment_credit = request.POST.get('payment_credit') == 'on'
            
            order.payment_amount_cash = Decimal(request.POST.get('payment_amount_cash', '0') or '0')
            order.payment_amount_check = Decimal(request.POST.get('payment_amount_check', '0') or '0')
            order.payment_amount_credit = Decimal(request.POST.get('payment_amount_credit', '0') or '0')
            
            # ອາກອນ
            order.tax_percent = Decimal(request.POST.get('tax_percent', '0') or '0')
            
            # ບັນທຶກບິນ
            order.save()
            
            # ເພີ່ມລາຍການສິນຄ້າ
            item_count = int(request.POST.get('item_count', 0))
            for i in range(1, item_count + 1):
                description = request.POST.get(f'description_{i}', '').strip()
                if description:
                    item = OrderItem(order=order)
                    item.item_no = i
                    item.ref_code = request.POST.get(f'ref_code_{i}', '')
                    item.description = description
                    item.quantity = Decimal(request.POST.get(f'quantity_{i}', '1') or '1')
                    item.unit = request.POST.get(f'unit_{i}', 'ອັນ')
                    item.unit_price = Decimal(request.POST.get(f'unit_price_{i}', '0') or '0')
                    item.discount_percent = Decimal(request.POST.get(f'discount_percent_{i}', '0') or '0')
                    item.save()
            
            # ຄິດໄລ່ຍອດລວມທັງໝົດ
            order.calculate_totals()
            
            messages.success(request, f'ສ້າງບິນເລກທີ {order.invoice_no} ສຳເລັດແລ້ວ')
            return redirect('order_detail', invoice_no=order.invoice_no)
    
    # GET request
    context = {
        'today': timezone.now().date(),
    }
    return render(request, 'orders/order_form.html', context)


def order_update(request, invoice_no):
    """ແກ້ໄຂບິນ"""
    order = get_object_or_404(Order, invoice_no=invoice_no)
    
    if request.method == 'POST':
        with db_transaction.atomic():
            # ອັບເດດຂໍ້ມູນພື້ນຖານ
            order_date = request.POST.get('date')
            if order_date:
                order.date = order_date
            
            # ຂໍ້ມູນລູກຄ້າ
            order.customer_name = request.POST.get('customer_name', '')
            order.customer_phone = request.POST.get('customer_phone', '')
            order.customer_code = request.POST.get('customer_code', '')
            
            # ຂໍ້ມູນລົດ
            order.car_register_no = request.POST.get('car_register_no', '')
            order.car_province = request.POST.get('car_province', '')
            order.car_brand = request.POST.get('car_brand', '')
            order.car_model = request.POST.get('car_model', '')
            order.car_frame_no = request.POST.get('car_frame_no', '')
            order.car_color = request.POST.get('car_color', '')
            order.car_mileage = request.POST.get('car_mileage', '')
            
            # ຂໍ້ມູນພະນັກງານ
            order.mechanic_name = request.POST.get('mechanic_name', '')
            order.sale_representative = request.POST.get('sale_representative', '')
            
            # ຂໍ້ມູນການຈ່າຍເງິນ
            order.received_by = request.POST.get('received_by', '')
            order.check_no = request.POST.get('check_no', '')
            check_date = request.POST.get('check_date', '')
            if check_date:
                order.check_date = check_date
            else:
                order.check_date = None
            order.bank_name = request.POST.get('bank_name', '')
            order.bank_branch = request.POST.get('bank_branch', '')
            
            # ວິທີການຈ່າຍເງິນ
            order.payment_cash = request.POST.get('payment_cash') == 'on'
            order.payment_check = request.POST.get('payment_check') == 'on'
            order.payment_credit = request.POST.get('payment_credit') == 'on'
            
            order.payment_amount_cash = Decimal(request.POST.get('payment_amount_cash', '0') or '0')
            order.payment_amount_check = Decimal(request.POST.get('payment_amount_check', '0') or '0')
            order.payment_amount_credit = Decimal(request.POST.get('payment_amount_credit', '0') or '0')
            
            # ອາກອນ
            order.tax_percent = Decimal(request.POST.get('tax_percent', '0') or '0')
            
            order.save()
            
            # ລຶບລາຍການເກົ່າທັງໝົດ ແລະ ເພີ່ມໃໝ່ (ຫຼືອັບເດດ)
            order.items.all().delete()
            
            item_count = int(request.POST.get('item_count', 0))
            for i in range(1, item_count + 1):
                description = request.POST.get(f'description_{i}', '').strip()
                if description:
                    item = OrderItem(order=order)
                    item.item_no = i
                    item.ref_code = request.POST.get(f'ref_code_{i}', '')
                    item.description = description
                    item.quantity = Decimal(request.POST.get(f'quantity_{i}', '1') or '1')
                    item.unit = request.POST.get(f'unit_{i}', 'ອັນ')
                    item.unit_price = Decimal(request.POST.get(f'unit_price_{i}', '0') or '0')
                    item.discount_percent = Decimal(request.POST.get(f'discount_percent_{i}', '0') or '0')
                    item.save()
            
            # ຄິດໄລ່ຍອດລວມທັງໝົດ
            order.calculate_totals()
            
            messages.success(request, f'ອັບເດດບິນເລກທີ {order.invoice_no} ສຳເລັດແລ້ວ')
            return redirect('order_detail', invoice_no=order.invoice_no)
    
    # GET request
    items = order.items.all().order_by('item_no')
    context = {
        'order': order,
        'items': items,
        'is_update': True,
        'today': timezone.now().date(),
    }
    return render(request, 'orders/order_form.html', context)


def order_delete(request, invoice_no):
    """ລຶບບິນ"""
    order = get_object_or_404(Order, invoice_no=invoice_no)
    
    if request.method == 'POST':
        invoice_no_copy = order.invoice_no
        order.delete()
        messages.success(request, f'ລຶບບິນເລກທີ {invoice_no_copy} ສຳເລັດແລ້ວ')
        return redirect('order_list')
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_confirm_delete.html', context)


def order_print(request, invoice_no):
    """ພິມບິນ (ໃຊ້ template ທີ່ຖືກອອກແບບມາພິເສດສຳລັບການພິມ)"""
    order = get_object_or_404(Order, invoice_no=invoice_no)
    items = order.items.all().order_by('item_no')
    
    context = {
        'order': order,
        'items': items,
    }
    
    return render(request, 'orders/bill-detail-print.html', context)


def order_api_list(request):
    """API: ດຶງລາຍການບິນທັງໝົດ (JSON)"""
    orders = Order.objects.all().order_by('-date')
    
    data = []
    for order in orders:
        data.append({
            'invoice_no': order.invoice_no,
            'date': order.date.strftime('%Y-%m-%d'),
            'customer_name': order.customer_name,
            'customer_code': order.customer_code,
            'car_register_no': order.car_register_no,
            'net_amount_thb': float(order.net_amount_thb),
            'net_amount_lak': float(order.net_amount_lak),
            'net_amount_usd': float(order.net_amount_usd),
        })
    
    return JsonResponse({'orders': data})


def order_api_detail(request, invoice_no):
    """API: ດຶງລາຍລະອຽດບິນ (JSON)"""
    order = get_object_or_404(Order, invoice_no=invoice_no)
    items = order.items.all().order_by('item_no')
    
    items_data = []
    for item in items:
        items_data.append({
            'item_no': item.item_no,
            'ref_code': item.ref_code,
            'description': item.description,
            'quantity': float(item.quantity),
            'unit': item.unit,
            'unit_price': float(item.unit_price),
            'discount_percent': float(item.discount_percent),
            'discount_amount': float(item.discount_amount),
            'amount': float(item.amount),
        })
    
    data = {
        'invoice_no': order.invoice_no,
        'date': order.date.strftime('%Y-%m-%d'),
        'customer_name': order.customer_name,
        'customer_phone': order.customer_phone,
        'customer_code': order.customer_code,
        'car_register_no': order.car_register_no,
        'car_province': order.car_province,
        'car_brand': order.car_brand,
        'car_model': order.car_model,
        'car_frame_no': order.car_frame_no,
        'car_color': order.car_color,
        'car_mileage': order.car_mileage,
        'mechanic_name': order.mechanic_name,
        'sale_representative': order.sale_representative,
        'subtotal_thb': float(order.subtotal_thb),
        'discount_thb': float(order.discount_thb),
        'tax_percent': float(order.tax_percent),
        'tax_amount_thb': float(order.tax_amount_thb),
        'net_amount_thb': float(order.net_amount_thb),
        'net_amount_lak': float(order.net_amount_lak),
        'net_amount_usd': float(order.net_amount_usd),
        'items': items_data,
    }
    
    return JsonResponse(data)
