from django.urls import path
from . import views

app_name = 'editor'

urlpatterns = [
    path('', views.editor_view, name='editor'),
    path('design/<int:design_id>/', views.editor_view, name='editor_design'),
    path('save_design/', views.save_design, name='save_design'),
    path('render_design/', views.render_design, name='render_design'),
]
