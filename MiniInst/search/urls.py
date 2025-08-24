from django.urls import path
from .views import search_view, profile_public_view

urlpatterns = [
    path("", search_view, name="search"),
    path("<str:username>/", profile_public_view, name="profile_public"),
]
