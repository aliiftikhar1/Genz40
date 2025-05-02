import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, ChatNotification
from django.db.models import Q

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'
            self.user = self.scope["user"]  # Add this line to store user
            
            # Reject unauthenticated connections
            if not self.user.is_authenticated:
                await self.close(code=4001)
                return

            # Verify room access
            if not await self.verify_room_access():
                await self.close(code=4003)
                return

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            print(f"Connection error: {str(e)}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Disconnection error: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'ping':
                await self.send(json.dumps({'type': 'pong'}))
                return

            message = data.get('message', '').strip()
            if not message:
                return

            message_obj = await self.save_message(message)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': str(message_obj.id),
                    'message': message_obj.content,
                    'sender_id': str(self.user.id),  # Use self.user instead of message_obj.sender
                    'sender_name': await self.get_user_display_name(self.user),
                    'timestamp': message_obj.timestamp.isoformat(),
                    'is_read': message_obj.is_read
                }
            )

        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(str(e))
            print(f"Receive error: {str(e)}")

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat',
                'id': event['id'],
                'message': event['message'],
                'sender_id': event['sender_id'],
                'sender_name': event['sender_name'],
                'timestamp': event['timestamp'],
                'is_read': event['is_read']
            }))
        except Exception as e:
            print(f"Chat message error: {str(e)}")

    async def send_error(self, error):
        try:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error
            }))
        except Exception as e:
            print(f"Error sending error: {str(e)}")

    @database_sync_to_async
    def verify_room_access(self):
        try:
            return ChatRoom.objects.filter(
                id=self.room_id
            ).filter(
                Q(customer=self.user) | Q(admin=self.user)
            ).exists()
        except Exception as e:
            print(f"Room access verification error: {str(e)}")
            return False

    @database_sync_to_async
    def save_message(self, message):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            message_obj = Message.objects.create(
                chat_room=room,
                sender=self.user,
                content=message
            )
            room.update_timestamp()
            
            recipient = room.admin if self.user == room.customer else room.customer
            if recipient:
                notification, created = ChatNotification.objects.get_or_create(
                    user=recipient,
                    chat_room=room,
                    defaults={'count': 1}
                )
                if not created:
                    notification.increment()
            return message_obj
        except Exception as e:
            print(f"Message save error: {str(e)}")
            raise

    @database_sync_to_async
    def get_user_display_name(self, user):
        try:
            return user.get_full_name() or user.email
        except Exception as e:
            print(f"Get display name error: {str(e)}")
            return "Unknown"