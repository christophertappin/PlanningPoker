from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import WebsocketConsumer
import json

class PokerConsumer(WebsocketConsumer):
    def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['id']
        self.session_group_id = 'session_%s' % self.session_id

        async_to_sync(self.channel_layer.group_add)(
            self.session_group_id,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.session_group_id,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        vote = text_data_json['vote']

        async_to_sync(self.channel_layer.group_send)(
            self.session_group_id,
            {
                'type': 'vote',
                'vote': vote
            }
        )

    def vote(self, event):
        vote = event['vote']

        self.send(text_data=json.dumps({
            'vote': vote
        }))


# class SessionStateConsumer(SyncConsumer):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         log.info(kwargs)
#         self.session_id = self.scope['url_route']['kwargs']['id']
#         log.info(self.session_id)
#         self.votes = {0: 0, .5: 0, 1: 0, 2: 0, 3: 0, 5: 0, 8: 0, 13: 0}

#     def addVotes(self, event):
#         vote = event["vote"]
#         self.votes[vote] += 1
#         await self.channel_layer.send("")
