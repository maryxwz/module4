import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from direct.models import Direct, DirectMessage
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db.models import Q


User = get_user_model()

class DirectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.direct_id = self.scope['url_route']['kwargs']['direct_id']
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return

        allowed = await self.user_in_direct(self.user.id, self.direct_id)
        if not allowed:
            await self.close()
            return

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
        text = data.get('message', '').strip()
        if not text:
            return

        if not await self.user_in_direct(self.user.id, self.direct_id):
            await self.send(json.dumps({'error': 'not allowed'}))
            return

        msg = await self.save_message(self.direct_id, self.user.id, text)

        payload = {
            'type': 'chat_message',
            'id': str(msg.id),
            'message': msg.message,
            'sender_id': self.user.id,
            'created_at': msg.created_at.isoformat(),
        }

        await self.channel_layer.group_send(self.room_group_name, payload)

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

        try:
            sender = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            return None

        msg = DirectMessage.objects.create(
            direct=direct,
            sender=sender,
            message=message
        )

        return msg

    @database_sync_to_async
    def user_in_direct(self, user_id, direct_id):
        return Direct.objects.filter(
            Q(id=direct_id) & (Q(user1_id=user_id) | Q(user2_id=user_id))
        ).exists()
