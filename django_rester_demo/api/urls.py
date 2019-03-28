from django.urls import include, re_path
from django_rester.views import Login, Logout
from .views import TestView

urls_accounts = [
    re_path('login/?', Login.as_view(), name='login'),
    re_path('logout/?', Logout.as_view(), name='logout'),
]

urlpatterns = [
    re_path('account/?', include(urls_accounts), name='accounts'),
    re_path('test/?', TestView.as_view(), name='test'),
]
