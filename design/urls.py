from django.urls import path

from . import views

app_name = 'design'

urlpatterns = [
    path('', views.designs, name='designs'),
    path('new/', views.new, name='new'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('<int:pk>/edit/', views.edit, name='edit'),
]
