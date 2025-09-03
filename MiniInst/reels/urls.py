from django.urls import path

from . import views
urlpatterns = [
    path('create_reels/', views.create_reels, name='create_reels'),
    path('all_reels/', views.all_reels, name='all_reels'),
    path('delete_reel/<int:pk>/', views.delete_reels, name='delete_reel'),
]

