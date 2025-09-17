from django.urls import path

from . import views

urlpatterns = [
    path('create_story/', views.add_story, name='create_story'),
    path('all_stories/', views.all_stories, name='all_stories'),
    path('<int:id>/', views.view_story, name='current_story')
]
