from django.urls import path
from . import views

app_name = 'keditor'

urlpatterns = [
    path('', views.keditor_view, name='keditor'),
    path('<int:project_id>/', views.keditor_view, name='keditor_project'),
    path('save/', views.save_kids_project, name='save'),
    path('render/', views.render_kids_project, name='render'),
]
