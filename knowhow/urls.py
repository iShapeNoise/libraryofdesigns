from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'knowhow'

urlpatterns = [
    path('lod/', views.lod, name='lod'),
    path('cad/', views.cad, name='cad'),
    path('cam/', views.cam, name='cam'),
]
