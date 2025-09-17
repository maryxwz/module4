from django.urls import path
from .views import (
    register_view, profile_view, CustomLoginView,
    block_user_view, unblock_user_view,
    follow_user_view, unfollow_user_view,
    follow_request_accept_view, follow_request_reject_view,
    followers_list_view, following_list_view,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('profile/<str:username>', profile_view, name='profile'),
    path('profile/<str:username>/block/', block_user_view, name='block_user'),
    path('profile/<str:username>/unblock/', unblock_user_view, name='unblock_user'),
    path('u/<str:username>/follow/', follow_user_view, name='follow_user'),
    path('u/<str:username>/unfollow/', unfollow_user_view, name='unfollow_user'),
    path('u/requests/<int:pk>/accept/', follow_request_accept_view, name='follow_request_accept'),
    path('u/requests/<int:pk>/reject/', follow_request_reject_view, name='follow_request_reject'),
    path('u/<str:username>/followers/', followers_list_view, name='followers_list'),
    path('u/<str:username>/following/', following_list_view, name='following_list'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]