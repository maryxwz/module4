from django.urls import path

from . import views
urlpatterns = [
    path('create_reels/', views.create_reels, name='create_reels'),
    path('delete/<int:pk>/', views.delete_reels, name='delete_reels'),
    path('all_reels', views.all_reels, name='all_reels'),
    path('my/', views.all_reels_by_user, name='all_only_user_reels'),
    path('add_comment/<int:pk>/', views.add_comment, name='add_comment'),
    path('add_like/<int:pk>/', views.add_like, name='add_like'),
    path('all_reels_comments/<int:pk>/', views.all_reels_comments, name='all_reels_comments'),
]

