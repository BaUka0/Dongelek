from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
import chat.consumers
import notifications.consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\w+)/$', chat.consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/notifications/$', notifications.consumers.NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
