from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'knowhow'

urlpatterns = [
    path('<str:section>/', views.section_courses, name='section_courses'),
    path('<str:section>/<str:course_name>/', views.course_detail, name='course_detail'),
    path('<str:section>/<str:course_name>/overview/', views.course_overview, name='course_overview'),
]
