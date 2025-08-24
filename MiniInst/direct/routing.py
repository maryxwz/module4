from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/(?P<kind>direct|group)/(?P<chat_id>[^/]+)/$', consumers.DirectConsumer.as_asgi()),
]
