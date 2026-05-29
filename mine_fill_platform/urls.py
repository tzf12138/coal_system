from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from apps.core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('core/', include('apps.core.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
    path('lifecycle/', include('apps.lifecycle.urls')),
    path('equipment/', include('apps.equipment.urls')),
    path('training/', include('apps.training.urls')),
]
