# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django_rester.views import Login, Logout
from .views import TestView

urls_accounts = [
    url(r'^login/$', Login.as_view(), name='login'),
    url(r'^logout/$', Logout.as_view(), name='logout'),
]

urlpatterns = [
    url(r'^account/', include(urls_accounts, namespace='accounts')),
    url(r'^test/', TestView.as_view(), name='test'),

]
