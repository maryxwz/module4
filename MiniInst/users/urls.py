from django.urls import path
from . views import register_view, profile_view, CustomLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('profile/<str:username>', profile_view, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout')
]

