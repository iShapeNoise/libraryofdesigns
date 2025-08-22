from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_index, name='index'),
    path('category/<int:pk>/', views.category_view, name='category'),
    path('topic/<int:pk>/', views.topic_view, name='topic'),
    path('category/<int:category_pk>/new/', views.new_topic, name='new_topic'),
]
