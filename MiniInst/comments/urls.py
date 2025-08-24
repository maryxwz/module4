from django.urls import path
from .views import create_comment


urlpatterns = [
    path("<int:post_id>/create/", create_comment, name="create_comment"),
]

