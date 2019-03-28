from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    re_path('admin/?', admin.site.urls),
    path('api/', include("api.urls"), name='api'),
]
