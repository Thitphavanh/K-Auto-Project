from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('report/', views.report_view, name='report'),
    path('report/export/', views.export_report, name='export_report'),
]
