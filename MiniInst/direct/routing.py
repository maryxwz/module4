from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/direct/(?P<chat_id>[0-9a-f-]+)/$', consumers.DirectConsumer.as_asgi()),
]
