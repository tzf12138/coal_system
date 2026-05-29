from django.urls import path
from .views import ai_center, ar_guidance, dashboard, digital_twin, knowledge, smart_control

app_name = 'core'

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('knowledge/', knowledge, name='knowledge'),
    path('digital-twin/', digital_twin, name='digital_twin'),
    path('ai-center/', ai_center, name='ai_center'),
    path('smart-control/', smart_control, name='smart_control'),
    path('ar-guidance/', ar_guidance, name='ar_guidance'),
]
