from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Transaction, Brand
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)  # <--- import ເພີ່ມ
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
    categories = (
        Product.objects.values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

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
@csrf_exempt  # ຖ້າຂີ້ຄ້ານສົ່ງ CSRF token ໃນ Header ໃຫ້ໃສ່ໂຕນີ້ (ແຕ່ແນະນຳໃຫ້ສົ່ງດີກວ່າ)
def api_checkout(request):
    if request.method == "POST":
        try:
            # ແກະຂໍ້ມູນ JSON ທີ່ສົ່ງມາຈາກ JavaScript
            data = json.loads(request.body)
            cart_items = data.get("items", [])

            if not cart_items:
                return JsonResponse({"success": False, "error": "ກະຕ່າສິນຄ້າວ່າງເປົ່າ"})

            # ເລີ່ມການຕັດສະຕັອກ
            for item in cart_items:
                product = Product.objects.get(id=item["id"])
                qty = int(item["qty"])

                if product.quantity >= qty:
                    # 1. ຕັດສະຕັອກ
                    product.quantity -= qty
                    product.save()

                    # 2. ບັນທຶກລົງ Transaction
                    Transaction.objects.create(
                        product=product,
                        user=request.user,
                        transaction_type="OUT",  # ປະເພດຂາຍອອກ
                        amount=qty,
                        total_value=product.sell_price * qty,
                    )
                else:
                    return JsonResponse(
                        {"success": False, "error": f"ສິນຄ້າ {product.name} ໝົດ ຫຼື ບໍ່ພໍຂາຍ!"}
                    )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid Method"})


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
                    "category": product.category or "-",
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
