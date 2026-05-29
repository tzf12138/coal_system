from django.urls import path
from .views import (
    api_equipment_health, diagnosis_center, equipment_create, equipment_delete, equipment_detail,
    equipment_list, equipment_update, export_orders_excel, order_create, order_delete, order_update,
)

app_name = 'equipment'

urlpatterns = [
    path('', equipment_list, name='equipment_list'),
    path('create/', equipment_create, name='equipment_create'),
    path('item/<int:pk>/', equipment_detail, name='equipment_detail'),
    path('item/<int:pk>/edit/', equipment_update, name='equipment_update'),
    path('item/<int:pk>/delete/', equipment_delete, name='equipment_delete'),
    path('item/<int:pk>/health/', api_equipment_health, name='api_equipment_health'),
    path('item/<int:pk>/export-orders-excel/', export_orders_excel, name='export_orders_excel'),
    path('item/<int:equipment_pk>/order/create/', order_create, name='order_create_for_equipment'),
    path('order/create/', order_create, name='order_create'),
    path('order/<int:pk>/edit/', order_update, name='order_update'),
    path('order/<int:pk>/delete/', order_delete, name='order_delete'),
    path('diagnosis/', diagnosis_center, name='diagnosis_center'),
]
