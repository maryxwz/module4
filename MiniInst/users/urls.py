from django.urls import path
from . views import register_view, profile_view, CustomLoginView, block_user_view, unblock_user_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('profile/<str:username>', profile_view, name='profile'),
    path('profile/<str:username>/block/', block_user_view, name='block_user'),
    path('profile/<str:username>/unblock/', unblock_user_view, name='unblock_user'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout')
]
