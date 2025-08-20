from django.urls import path
from .views import register_view, profile_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
]
