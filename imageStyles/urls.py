from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'upload', views.upload, name="upload"),
    url(r'^images/private', views.images, name="images_private", kwargs={'scope': 'private'}),
    url(r'^images/public', views.images, name="images_public", kwargs={'scope': 'public'}),
    url(r'^images/detail/(?P<original_image_id>.*)', views.image_detail, name="image_detail"),
    url(r'^currentcount/private', views.currentcount, name="currentcount", kwargs={'scope': 'private'}),
    url(r'^currentcount/public', views.currentcount, name="currentcount", kwargs={'scope': 'public'}),
    url(r'^currentcount/(?P<original_image_id>.*)', views.currentcount, name="currentcount", kwargs={'scope': 'single_image'}),

    url('^$', views.index, name="index"),
]
