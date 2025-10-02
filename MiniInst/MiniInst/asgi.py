import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MiniInst.settings')

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

import direct.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            direct.routing.websocket_urlpatterns
        )
    ),
})