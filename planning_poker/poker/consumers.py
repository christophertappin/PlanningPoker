from channels.db import database_sync_to_async
from channels.consumer import SyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from collections import defaultdict
from .models import Vote

import json
import sys

class PokerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['id']
        client = self.scope['client']
        self.client = '{}:{}'.format(client[0], client[1])
        self.session_group_id = 'session_%s' % self.session_id

        await self.channel_layer.group_add(
            self.session_group_id,
            self.channel_name
        )

        await self.accept()

        # Send the current votes
        votes = await self._get_votes()
        await self.send(text_data=json.dumps({
                'type': 'votes',
                'votes': votes
            }))
        

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.session_group_id,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        vote = text_data_json['vote']
        await self._save_vote(vote)
        await self.sendCurrentState()
    
    async def sendCurrentState(self):
        votes = await self._get_votes()
        await self.channel_layer.group_send(
            self.session_group_id,
            {
                'type': 'votes',
                'votes': votes
            }
        )

    async def votes(self, event):
        vote = event['votes']

        await self.send(text_data=json.dumps({
            'votes': vote
        }))

    @database_sync_to_async
    def _save_vote(self, vote):
        try:
            vote_object = Vote.objects.get(session_id=self.session_id, client=self.client)
        except Vote.DoesNotExist:
            # Create it
            vote_object = Vote(session_id=self.session_id, client=self.client, value=vote)
        except Vote.MultipleObjectsReturned:
            # This shouldn't happen
            sys.exit("There shouldn't ever be more than one vote per client, per session!")
        else:
            vote_object.value = vote
        
        vote_object.save()

    @database_sync_to_async
    def _get_votes(self):
        votes = Vote.objects.filter(session_id=self.session_id)
        votes_dict = {}
        votes_dict = defaultdict(lambda:0, votes_dict)
        for vote in votes:
            votes_dict[str(vote.value).rstrip('.0')] += 1
        return {key: value for key, value in sorted(votes_dict.items(), key=lambda item: item[1], reverse=True)}

