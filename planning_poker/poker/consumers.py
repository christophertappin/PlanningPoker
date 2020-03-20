from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import WebsocketConsumer
from collections import defaultdict
# from models import Vote
from .models import Vote
import json
# import logging
import sys

# logger = logging.getLogger(__name__)

class PokerConsumer(WebsocketConsumer):
    def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['id']
        # self.session_key = self.scope['session']['session_key'].save()
        # print(str(self.scope['client']))
        # self.client = '%s:%s' % (self.scope['client'][0]], self.scope['client'][1])
        # user = self.scope['user']
        client = self.scope['client']
        self.client = '{}:{}'.format(client[0], client[1])
        print(self.client)
        self.session_group_id = 'session_%s' % self.session_id

        async_to_sync(self.channel_layer.group_add)(
            self.session_group_id,
            self.channel_name
        )
        self.accept()
        
        self.sendCurrentState()
        

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.session_group_id,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        vote = text_data_json['vote']
        self._save_vote(vote)
        self.sendCurrentState()
    
    def sendCurrentState(self):
        votes = self._get_votes()
        async_to_sync(self.channel_layer.group_send)(
            self.session_group_id,
            {
                'type': 'votes',
                'votes': votes
            }
        )

    def votes(self, event):
        vote = event['votes']

        self.send(text_data=json.dumps({
            'votes': vote
        }))

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

    def _get_votes(self):
        votes = Vote.objects.filter(session_id=self.session_id)
        votes_dict = {}
        votes_dict = defaultdict(lambda:0, votes_dict)
        for vote in votes:
            votes_dict[str(vote.value)] += 1
        return {key: value for key, value in sorted(votes_dict.items(), key=lambda item: item[1], reverse=True)}


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
