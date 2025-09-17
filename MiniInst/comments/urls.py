from django.urls import path
from .views import api_comments

app_name = "comments"

urlpatterns = [
    path("api/", api_comments, name="api"),
]

