import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from direct.models import Direct, DirectMessage, GroupChat, GroupMessage
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db.models import Q


User = get_user_model()

class DirectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.kind = self.scope['url_route']['kwargs']['kind']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return

        allowed = await self.user_allowed(self.user.id, self.kind, self.chat_id)
        if not allowed:
            await self.close()
            return

        self.room_group_name = f'{self.kind}_{self.chat_id}'

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

        if not await self.user_allowed(self.user.id, self.kind, self.chat_id):
            await self.send(json.dumps({'error': 'not allowed'}))
            return

        msg = await self.save_message(self.kind, self.chat_id, self.user.id, text)
        if not msg:
            await self.send(json.dumps({'error': 'save_failed'}))
            return
        
        payload = {
            'type': 'chat_message',
            'id': str(msg['id']),
            'message': msg['message'],
            'sender_id': msg['sender_id'],
            'sender_username': msg.get('sender_username'),
            'created_at': msg['created_at'],
            'created_time': msg['created_time'],
        }

        await self.channel_layer.group_send(self.room_group_name, payload)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))

    @sync_to_async
    def save_message(self, kind, chat_id, sender_id, message):
        
        try:
            sender = User.objects.get(id=sender_id)
        except User.DoesNotExist:
            return None
        
        if kind == 'direct':
            try:
                direct = Direct.objects.get(id=chat_id)
            except Direct.DoesNotExist:
                return None
            msg = DirectMessage.objects.create(
                direct=direct,
                sender=sender,
                message=message
            )
        elif kind == 'group':
            try:
                group = GroupChat.objects.get(id=chat_id)
            except GroupChat.DoesNotExist:
                return None        
            
            msg = GroupMessage.objects.create(
                group_chat=group,
                sender=sender,
                message=message
            )
        else:
            return None
        return {
            'id': msg.id,
            'message': msg.message,
            'sender_id': msg.sender.id,
            'sender_username': getattr(msg.sender, 'username', None),
            'created_at': msg.created_at.isoformat(),
            'created_time': msg.created_at.strftime('%H:%M'),
        }

    @database_sync_to_async
    def user_allowed(self, user_id, kind, chat_id):
        if kind == 'direct':
            return Direct.objects.filter(
                Q(id=chat_id) & (Q(user1_id=user_id) | Q(user2_id=user_id))
            ).exists()
        elif kind == 'group':
            return GroupChat.objects.filter(id=chat_id, members__id=user_id).exists()
        return False