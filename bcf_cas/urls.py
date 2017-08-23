from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'user/login$', views.login),
    url(r'user/logout$', views.logout),
]
