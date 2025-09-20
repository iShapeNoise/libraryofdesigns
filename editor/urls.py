from django.urls import path
from . import views


app_name = 'editor'  

urlpatterns = [  
    path('', views.editor_view, name='editor'),  
    path('<int:design_id>/', views.editor_view, name='editor_with_design'),  
    path('save/', views.save_design, name='save_design'),  
    path('render/', views.render_design, name='render_design'),  
]
