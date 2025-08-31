import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from direct.models import Direct, DirectMessage, GroupChat, GroupMessage
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
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data or "{}")
        action = data.get('action')

        if not action:
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
                'edited': msg.get('edited', False),
            }
            await self.channel_layer.group_send(self.room_group_name, payload)
            return

        if action == 'edit':
            message_id = data.get('id')
            new_text = data.get('message', '').strip()
            if not message_id or new_text == '':
                await self.send(json.dumps({'error': 'invalid_edit_payload'}))
                return
            edited = await self.edit_message(self.kind, self.chat_id, self.user.id, message_id, new_text)
            if not edited:
                await self.send(json.dumps({'error': 'edit_failed'}))
                return
            payload = {
                'type': 'chat_message_edit',
                'id': str(message_id),
                'message': new_text,
                'sender_id': self.user.id,
                'edited': True,
            }
            await self.channel_layer.group_send(self.room_group_name, payload)
            return

        if action == 'delete':
            message_id = data.get('id')
            if not message_id:
                await self.send(json.dumps({'error': 'invalid_delete_payload'}))
                return
            deleted = await self.delete_message(self.kind, self.chat_id, self.user.id, message_id)
            if not deleted:
                await self.send(json.dumps({'error': 'delete_failed'}))
                return
            payload = {'type': 'chat_message_delete', 'id': str(message_id)}
            await self.channel_layer.group_send(self.room_group_name, payload)
            return

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'id': event.get('id'),
            'message': event.get('message'),
            'sender_id': event.get('sender_id'),
            'sender_username': event.get('sender_username'),
            'created_at': event.get('created_at'),
            'created_time': event.get('created_time'),
            'edited': event.get('edited', False),
        }))

    async def chat_message_edit(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message_edit',
            'id': event.get('id'),
            'message': event.get('message'),
            'sender_id': event.get('sender_id'),
            'edited': event.get('edited', True),
        }))

    async def chat_message_delete(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message_delete',
            'id': event.get('id'),
        }))

    @database_sync_to_async
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
            msg = DirectMessage.objects.create(direct=direct, sender=sender, message=message)
        elif kind == 'group':
            try:
                group = GroupChat.objects.get(id=chat_id)
            except GroupChat.DoesNotExist:
                return None
            msg = GroupMessage.objects.create(group_chat=group, sender=sender, message=message)
        else:
            return None
        return {
            'id': msg.id,
            'message': msg.message,
            'sender_id': msg.sender.id,
            'sender_username': getattr(msg.sender, 'username', None),
            'created_at': msg.created_at.isoformat(),
            'created_time': msg.created_at.strftime('%H:%M'),
            'edited': getattr(msg, 'edited', False),
        }

    @database_sync_to_async
    def user_allowed(self, user_id, kind, chat_id):
        if kind == 'direct':
            return Direct.objects.filter(Q(id=chat_id) & (Q(user1_id=user_id) | Q(user2_id=user_id))).exists()
        if kind == 'group':
            return GroupChat.objects.filter(id=chat_id, members__id=user_id).exists()
        return False

    @database_sync_to_async
    def edit_message(self, kind, chat_id, user_id, message_id, new_text):
        try:
            if kind == 'direct':
                msg = DirectMessage.objects.get(id=message_id, direct_id=chat_id)
            elif kind == 'group':
                msg = GroupMessage.objects.get(id=message_id, group_chat_id=chat_id)
            else:
                return None
        except (DirectMessage.DoesNotExist, GroupMessage.DoesNotExist,
                DirectMessage.MultipleObjectsReturned, GroupMessage.MultipleObjectsReturned):
            return None
        if msg.sender_id != user_id:
            return None
        fields_to_update = ['message']
        if hasattr(msg, 'edited'):
            msg.edited = True
            fields_to_update.append('edited')
        msg.message = new_text
        msg.save(update_fields=fields_to_update)
        return {'edited': msg.edited}

    @database_sync_to_async
    def delete_message(self, kind, chat_id, user_id, message_id):
        try:
            if kind == 'direct':
                msg = DirectMessage.objects.get(id=message_id, direct_id=chat_id)
            elif kind == 'group':
                msg = GroupMessage.objects.get(id=message_id, group_chat_id=chat_id)
            else:
                return False
        except (DirectMessage.DoesNotExist, GroupMessage.DoesNotExist):
            return False
        if msg.sender_id != user_id:
            return False
        msg.delete()
        return True
