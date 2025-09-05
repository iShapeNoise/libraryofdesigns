from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'knowhow'

urlpatterns = [
    path('lod/', views.lod, name='lod'),
    path('cad/', views.cad, name='cad'),
    path('cam/', views.cam, name='cam'),
    path('cad/<str:course_name>/', views.course_detail, {'section': 'cad'}, name='cad_course_detail'),
    path('lod/<str:course_name>/', views.course_detail, {'section': 'lod'}, name='lod_course_detail'),
    path('cam/<str:course_name>/', views.course_detail, {'section': 'cam'}, name='cam_course_detail'),
]
