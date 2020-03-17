from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
import poker.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            poker.routing.websocket_urlpatterns
        )
    ),
    # 'channel': ChannelNameRouter(
    #     poker.routing.channel_consumer
    # ),
})