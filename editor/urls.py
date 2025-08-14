from django.urls import path
from . import views

app_name = 'editor'

urlpatterns = [
    path('', views.editor_view, name='editor'),
    path('project/<int:project_id>/', views.editor_view, name='editor_project'),
    path('save_project/', views.save_project, name='save_project'),
    path('render_project/', views.render_project, name='render_project'),
]
