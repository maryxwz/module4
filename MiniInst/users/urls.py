from django.urls import path
from . import views
from .views import CustomLoginView

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("profile/<str:username>", views.profile_view, name="profile"),
    path("follow/<str:username>", views.follow_user_view, name="follow_user"),
    path("unfollow/<str:username>", views.unfollow_user_view, name="unfollow_user"),
    path("block/<str:username>", views.block_user_view, name="block_user"),
    path("unblock/<str:username>", views.unblock_user_view, name="unblock_user"),
    path("requests/incoming/<str:username>", views.follow_requests_incoming_view, name="follow_requests_incoming"),
    path("requests/outgoing/<str:username>", views.follow_requests_outgoing_view, name="follow_requests_outgoing"),
    path("requests/accept/<int:pk>", views.follow_request_accept_view, name="follow_request_accept"),
    path("requests/reject/<int:pk>", views.follow_request_reject_view, name="follow_request_reject"),
    path("requests/cancel/<str:username>", views.follow_request_cancel_view, name="follow_request_cancel"),
    path("followers/<str:username>", views.followers_list_view, name="followers_list"),
    path("following/<str:username>", views.following_list_view, name="following_list"),
    path("settings", views.account_settings_view, name="settings"),
    path("login/", CustomLoginView.as_view(template_name="registration/login.html"), name="login"),
]