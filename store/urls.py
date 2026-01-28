from django.urls import path
from . import views


urlpatterns = [
    path("", views.home_view, name="home"),  # Home page
    path(
        "products/", views.product_list_view, name="product-list"
    ),  # Products list page
    path("product/<slug:slug>/", views.product_detail_view, name="product-detail"),
    path("pos/", views.pos_view, name="pos"),
    path("stock-in/", views.stock_in_view, name="stock-in"),
    path("dashboard/", views.dashboard_view, name="dashboard"),

    # API Endpoints
    path("api/get-product/", views.api_get_product, name="api_get_product"),
    path("api/checkout/", views.api_checkout, name="api_checkout"),
    path("api/stock-in/", views.api_stock_in, name="api_stock_in"),
    path("api/search-customer/", views.api_search_customer, name="api_search_customer"),
    path("api/search-product/", views.api_search_product, name="api_search_product"),
    path("api/manual-checkout/", views.api_manual_checkout, name="api_manual_checkout"),
    path("api/orders/", views.order_api_list, name="order_api_list"),
    path("api/orders/<str:invoice_no>/", views.order_api_detail, name="order_api_detail"),
    path("api/save-customer/", views.api_save_customer, name="api_save_customer"),

    # Bill/Invoice Management
    path("input-bill/", views.input_bill_view, name="input-bill"),
    path("customer-registration/", views.customer_registration_view, name="customer-registration"),
    path("bill/<int:order_id>/", views.bill_detail_view, name="bill-detail"),

    # Order Management
    path("orders/", views.order_list, name="order_list"),
    path("orders/create/", views.order_create, name="order_create"),
    path("orders/<str:invoice_no>/", views.order_detail, name="order_detail"),
    path("orders/<str:invoice_no>/update/", views.order_update, name="order_update"),
    path("orders/<str:invoice_no>/delete/", views.order_delete, name="order_delete"),
    path("orders/<str:invoice_no>/print/", views.order_print, name="order_print"),

    # Quotation System
    path("quotations/", views.quotation_list, name="quotation_list"),
    path("quotations/create/", views.quotation_create, name="quotation_create"),
    path("quotations/<int:pk>/", views.quotation_detail, name="quotation_detail"),
    path("quotations/<int:pk>/delete/", views.quotation_delete, name="quotation_delete"),
    path("quotations/<int:pk>/to-order/", views.quotation_to_order, name="quotation_to_order"),
]
