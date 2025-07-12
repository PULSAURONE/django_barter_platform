"""
URL configuration for bpp_project project.
...
"""
from django.contrib import admin
from django.urls import path, include
from users.views import register

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/register/', register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('ads.urls')),
]