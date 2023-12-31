import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')

from django.core.asgi import get_asgi_application

django_asgi_app=get_asgi_application()

from channels.auth import AuthMiddlewareStack
from apps.chat import routing
from channels.routing import ProtocolTypeRouter,URLRouter

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket":AuthMiddlewareStack(
            URLRouter(
                routes=routing.websocket_urlpatterns
            )
    ),
})