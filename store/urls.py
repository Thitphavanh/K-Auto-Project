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
    path("api/get-product/", views.api_get_product, name="api_get_product"),
    path("api/checkout/", views.api_checkout, name="api_checkout"),
    path("api/stock-in/", views.api_stock_in, name="api_stock_in"),
]
