from django.urls import path
from .views import course_list

app_name = 'training'

urlpatterns = [
    path('', course_list, name='course_list'),
]
