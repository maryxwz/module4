from django.urls import path
from .views import register_view, profile_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path("repost/<int:post_id>/", views.repost_post, name="repost_post"),
    path("<str:username>/reposts/", views.user_reposts, name="user_reposts"),
]



