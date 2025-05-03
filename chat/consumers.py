# Consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, ChatNotification
from django.db.models import Q
from asgiref.sync import async_to_sync

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'
            self.user = self.scope["user"]
            
            if not self.user.is_authenticated:
                await self.close(code=4001)
                return

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
                    'sender_id': str(self.user.id),
                    'sender_name': await self.get_user_display_name(self.user),
                    'sender_role': 'admin' if self.user.is_staff else 'customer',
                    'timestamp': message_obj.timestamp.isoformat(),
                    'is_read': message_obj.is_read,
                    'room_id': str(self.room_id),
                    'room_name': (await self.get_room_name()) or 'Support'
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
                'sender_role': event['sender_role'],
                'timestamp': event['timestamp'],
                'is_read': event['is_read'],
                'room_id': event['room_id'],
                'room_name': event['room_name']
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
        except ValueError as e:
            print(f"Room access verification error: {str(e)}")
            return False
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

    @database_sync_to_async
    def get_room_name(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            if self.user.is_staff:
                return f"{room.customer.get_full_name() or room.customer.email} - {room.subject}"
            return room.subject
        except Exception as e:
            print(f"Get room name error: {str(e)}")
            return None

class GlobalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope["user"]
            self.group_name = f'user_{self.user.id}_global'

            if not self.user.is_authenticated:
                await self.close(code=4001)
                return

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

            # Join all room groups the user is part of
            await self.join_room_groups()
        except Exception as e:
            print(f"Global connection error: {str(e)}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            await self.leave_room_groups()
        except Exception as e:
            print(f"Global disconnection error: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'ping':
                await self.send(json.dumps({'type': 'pong'}))
                return

            if data.get('type') == 'typing':
                room_id = data.get('room_id')
                if room_id:
                    await self.channel_layer.group_send(
                        f'chat_{room_id}',
                        {
                            'type': 'typing_message',
                            'is_typing': data.get('is_typing', False),
                            'sender_id': str(self.user.id)
                        }
                    )
                return

            message = data.get('message', '').strip()
            room_id = data.get('room_id')
            if message and room_id:
                message_obj = await self.save_message(message, room_id)
                
                await self.channel_layer.group_send(
                    f'chat_{room_id}',
                    {
                        'type': 'chat_message',
                        'id': str(message_obj.id),
                        'message': message_obj.content,
                        'sender_id': str(self.user.id),
                        'sender_name': await self.get_user_display_name(self.user),
                        'sender_role': 'admin' if self.user.is_staff else 'customer',
                        'timestamp': message_obj.timestamp.isoformat(),
                        'is_read': message_obj.is_read,
                        'room_id': room_id,
                        'room_name': (await self.get_room_name(room_id)) or 'Support'
                    }
                )

        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(str(e))
            print(f"Global receive error: {str(e)}")

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat',
                'id': event['id'],
                'message': event['message'],
                'sender_id': event['sender_id'],
                'sender_name': event['sender_name'],
                'sender_role': event['sender_role'],
                'timestamp': event['timestamp'],
                'is_read': event['is_read'],
                'room_id': event['room_id'],
                'room_name': event['room_name']
            }))
        except Exception as e:
            print(f"Global chat message error: {str(e)}")

    async def typing_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': event['is_typing'],
                'sender_id': event['sender_id']
            }))
        except Exception as e:
            print(f"Typing message error: {str(e)}")

    async def send_error(self, error):
        try:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': error
            }))
        except Exception as e:
            print(f"Error sending error: {str(e)}")

    @database_sync_to_async
    def join_room_groups(self):
        try:
            rooms = ChatRoom.objects.filter(
                Q(customer=self.user) | Q(admin=self.user)
            )
            for room in rooms:
                async_to_sync(self.channel_layer.group_add)(
                    f'chat_{room.id}',
                    self.channel_name
                )
        except Exception as e:
            print(f"Join room groups error: {str(e)}")

    @database_sync_to_async
    def leave_room_groups(self):
        try:
            rooms = ChatRoom.objects.filter(
                Q(customer=self.user) | Q(admin=self.user)
            )
            for room in rooms:
                async_to_sync(self.channel_layer.group_discard)(
                    f'chat_{room.id}',
                    self.channel_name
                )
        except Exception as e:
            print(f"Leave room groups error: {str(e)}")

    @database_sync_to_async
    def save_message(self, message, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
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

    @database_sync_to_async
    def get_room_name(self, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            if self.user.is_staff:
                return f"{room.customer.get_full_name() or room.customer.email} - {room.subject}"
            return room.subject
        except Exception as e:
            print(f"Get room name error: {str(e)}")
            return None