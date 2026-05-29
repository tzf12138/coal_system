from django.urls import path
from .views import (
    alert_center, api_process_trend, api_realtime, process_create, process_delete,
    process_detail, process_list, process_update, sensor_center, sensor_create,
    sensor_delete, sensor_update,
)

app_name = 'monitoring'

urlpatterns = [
    path('', process_list, name='process_list'),
    path('create/', process_create, name='process_create'),
    path('process/<int:pk>/', process_detail, name='process_detail'),
    path('process/<int:pk>/edit/', process_update, name='process_update'),
    path('process/<int:pk>/delete/', process_delete, name='process_delete'),
    path('process/<int:process_pk>/sensor/create/', sensor_create, name='sensor_create_for_process'),
    path('sensor/<int:pk>/edit/', sensor_update, name='sensor_update'),
    path('sensor/<int:pk>/delete/', sensor_delete, name='sensor_delete'),
    path('sensors/', sensor_center, name='sensor_center'),
    path('sensor/create/', sensor_create, name='sensor_create'),
    path('alerts/', alert_center, name='alert_center'),
    path('api/realtime/', api_realtime, name='api_realtime'),
    path('api/process/<int:pk>/trend/', api_process_trend, name='api_process_trend'),
]
