from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from collections import defaultdict
from .models import Vote

import json
import re
import sys


class PokerConsumer(AsyncWebsocketConsumer):
    '''
    An Asynchronous websocket consumer for receiving data from and broadcasting updates to clients.
    '''

    async def connect(self):
        '''Handle a websocket connection.'''

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
        '''Removes a client from the group when they disconnect.'''

        await self.channel_layer.group_discard(
            self.session_group_id,
            self.channel_name
        )

    async def receive(self, text_data):
        '''Save data received from the client and broadcast to subscribers.'''

        text_data_json = json.loads(text_data)
        vote = text_data_json['vote']
        await self._save_vote(vote)
        await self.send_current_state()

    async def send_current_state(self):
        '''Gets the current votes and broadcasts to subscribers.'''

        votes = await self._get_votes()
        await self.channel_layer.group_send(
            self.session_group_id,
            {
                'type': 'votes',
                'votes': votes
            }
        )

    async def votes(self, event):
        '''Send the votes to subscribers'''

        vote = event['votes']

        await self.send(text_data=json.dumps({
            'votes': vote
        }))

    @database_sync_to_async
    def _save_vote(self, vote):
        '''Saves the vote to the database.'''

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
        '''Get the votes from the database.'''
        
        votes = Vote.objects.filter(session_id=self.session_id)
        votes_dict = {}
        votes_dict = defaultdict(lambda: 0, votes_dict)
        for vote in votes:
            value = str(vote.value)
            # Remove trailing .0
            value = re.sub(r"\.0$", "", value)
            votes_dict[value] += 1
        return {key: value for key, value in sorted(votes_dict.items(), key=lambda item: item[1], reverse=True)}
