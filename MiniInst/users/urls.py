from django.urls import path
from .views import (
    register_view, profile_view, CustomLoginView,
    block_user_view, unblock_user_view,
    follow_user_view, unfollow_user_view,
    follow_request_accept_view, follow_request_reject_view,
    followers_list_view, following_list_view,
    follow_requests_incoming_view, follow_requests_outgoing_view,
    follow_request_cancel_view, account_settings_view,
)
from django.contrib.auth import views as auth_views

app_name = "users"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", CustomLoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("profile/<str:username>", profile_view, name="profile"),
    path("profile/<str:username>/block/", block_user_view, name="block_user"),
    path("profile/<str:username>/unblock/", unblock_user_view, name="unblock_user"),
    path("u/<str:username>/follow/", follow_user_view, name="follow_user"),
    path("u/<str:username>/unfollow/", unfollow_user_view, name="unfollow_user"),
    path("u/requests/<int:pk>/accept/", follow_request_accept_view, name="follow_request_accept"),
    path("u/requests/<int:pk>/reject/", follow_request_reject_view, name="follow_request_reject"),
    path("u/<str:username>/requests/incoming/", follow_requests_incoming_view, name="follow_requests_incoming"),
    path("u/<str:username>/requests/outgoing/", follow_requests_outgoing_view, name="follow_requests_outgoing"),
    path("u/<str:username>/requests/cancel/", follow_request_cancel_view, name="follow_request_cancel"),
    path("settings/", account_settings_view, name="settings"),
    path("u/<str:username>/followers/", followers_list_view, name="followers_list"),
    path("u/<str:username>/following/", following_list_view, name="following_list"),
]