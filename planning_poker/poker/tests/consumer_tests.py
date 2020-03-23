import pytest
import json
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.conf.urls import url
from poker.consumers import PokerConsumer


@pytest.mark.django_db
class TestPokerConsumer:

    @pytest.fixture()
    async def communicator(self, db):
        application = URLRouter([
            url(r'testws/session/(?P<id>\w+)/$', PokerConsumer),
        ])

        id = "aRandomId"
        client = ("0.0.0.0", 1)
        communicator = WebsocketCommunicator(application, "/testws/session/" + id + "/")
        communicator.scope['client'] = client
        connected, subprotocol = await communicator.connect()
        assert connected
        return communicator

    @pytest.mark.asyncio
    async def test_consumer_connect(self, communicator):
        response = await communicator.receive_from()
        assert response is not None
        json_response = json.loads(response)
        assert len(json_response['votes']) == 0
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_consumer_send(self, communicator):
        # Wait for initial state to be send
        await communicator.receive_from()

        await communicator.send_json_to({ "vote": "1" })
        response = await communicator.receive_from()
        response_json = json.loads(response)
        assert len(response_json['votes']) == 1
        await communicator.disconnect()
