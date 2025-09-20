from django.urls import path
from . import views


app_name = "posts"

urlpatterns = [
    path("save/<int:post_id>/", views.save_post, name="save_post"),
    path("saved/", views.saved_posts_view, name="saved_posts"),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('<int:pk>/update/', views.post_update, name='post_update'),

    path('repost/<int:post_id>/', views.repost_post, name='repost_post'),
    path('reposts/friends/', views.friends_reposts, name='friends_reposts'),
    path("reposts/<str:username>/", views.user_reposts, name="user_reposts"),


]
