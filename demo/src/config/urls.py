# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('account.urls', namespace='account')),
    url(r'^contact/', include('contact.urls', namespace='contact')),
    url(r'^ware/', include('ware.urls', namespace='ware')),
    url(r'^sale/', include('sale.urls', namespace='sale')),
    url(r'^api/', include('api.urls', namespace='api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
