import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dongelek.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Import the websocket_urlpatterns from routing.py
from Dongelek.routing import websocket_urlpatterns

# Create the ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})