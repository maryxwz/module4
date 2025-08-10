from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/direct/(?P<direct_id>[^/]+)/$', consumers.DirectConsumer.as_asgi()),
]
