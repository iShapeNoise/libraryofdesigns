from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.browse_categories, name='browse_categories'),
    path('categories/<int:category_id>/', views.browse_categories, name='browse_category'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html',
        authentication_form=LoginForm), name='login'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('license/', views.license, name='license'),
    path('terms_of_use/', views.terms_of_use, name='terms_of_use'),
    path('about_lod/', views.about_lod, name='about_lod'),
    path('contact/', views.contact, name='contact'),
]
