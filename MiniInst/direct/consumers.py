import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from direct.models import Direct, DirectMessage
from asgiref.sync import sync_to_async

User = get_user_model()

class DirectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.direct_id = self.scope['url_route']['kwargs']['direct_id']
        self.room_group_name = f'direct_{self.direct_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender_id']

        await self.save_message(self.direct_id, sender_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))

    @sync_to_async
    def save_message(self, direct_id, sender_id, message):
        try:
            direct = Direct.objects.get(id=direct_id)
        except Direct.DoesNotExist:
            return

        sender = User.objects.get(id=sender_id)

        DirectMessage.objects.create(
            direct=direct,
            sender=sender,
            message=message
        )
