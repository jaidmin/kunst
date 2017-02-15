from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^upload',views.upload, name="upload"),
    url(r'^images', views.images, name="images"),


    url(r'^$', views.index, name="index")

]