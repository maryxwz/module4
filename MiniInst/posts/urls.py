from django.urls import path
from .views import save_post, saved_posts_view

urlpatterns = [
    path("save/<int:post_id>/", save_post, name="save_post"),
    path("saved/", saved_posts_view, name="saved_posts"),
]
