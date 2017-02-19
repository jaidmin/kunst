from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'upload', views.upload, name="upload"),
    url(r'^images/private', views.images_private, name="images_private"),
    url(r'^images/public', views.images_public, name="images_public"),

    url(r'^currentcount/private', views.currentcount_private, name="currentcount_private"),
    url(r'^currentcount/public', views.currentcount_public, name="currentcount_public"),

    url('^$', views.index, name="index"),
]
