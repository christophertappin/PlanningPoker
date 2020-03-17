from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/session/(?P<id>\w+)/$', consumers.PokerConsumer),
]

# channel_consumer = {
#     "state_consumer": consumers.SessionStateConsumer
# }