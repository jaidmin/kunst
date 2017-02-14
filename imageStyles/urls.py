from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^upload',views.upload, name="upload"),
    url(r'^images', views.images, name="images"),
    url(r'^', views.index, name="index")

]