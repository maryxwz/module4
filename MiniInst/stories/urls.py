from django.urls import path

from . import views

urlpatterns = [
    path('create_story/', views.add_story, name='create_story'),
    path('all_stories/', views.all_stories, name='all_stories'),
    path('delete_story/<int_pk>/', views.delete_story, name='delete_story'),
    path('create_reels/', views.add_mini_reels, name='create_reels'),
    path('all_reels/', views.all_reels, name='all_reels'),
    path('delete_reel/<int_pk>/', views.delete_reels, name='delete_reel'),
]

