from django.urls import path

from . import views

app_name = 'design'

urlpatterns = [
    path('', views.designs, name='designs'),
    path('new/', views.new, name='new'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('tag/<slug:tag_slug>/', views.designs_by_tag, name='designs_by_tag'),
    path('<int:pk>/download/', views.download_design, name='download'),
    path('bom-search/', views.bom_search, name='bom_search'),
]
