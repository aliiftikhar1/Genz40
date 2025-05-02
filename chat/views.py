from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, ChatNotification
from .serializers import ChatRoomSerializer, MessageSerializer, ChatNotificationSerializer
from django.db.models import Q, Max
from django.utils import timezone

User = get_user_model()

class ChatRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(customer=user) | Q(admin=user)
        ).annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time', '-updated_at')

    def create(self, request, *args, **kwargs):
        try:
            customer = request.user
            admin = User.objects.filter(is_staff=True).first()
            subject = request.data.get('subject', 'General Inquiry')
            
            # Create new chat room with subject
            room_name = f"chat_{customer.id}_{admin.id if admin else '0'}_{timezone.now().timestamp()}"
            chat_room = ChatRoom.objects.create(
                customer=customer,
                admin=admin,
                room_name=room_name,
                subject=subject,
                is_active=True
            )
            
            serializer = self.get_serializer(chat_room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return Message.objects.filter(
            chat_room_id=room_id
        ).select_related('sender').order_by('timestamp')

    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        chat_room = ChatRoom.objects.get(id=room_id)
        message = serializer.save(
            sender=self.request.user, 
            chat_room=chat_room
        )
        
        # Update chat room timestamp
        chat_room.update_timestamp()
        
        # Update notification
        if self.request.user == chat_room.customer:
            recipient = chat_room.admin
        else:
            recipient = chat_room.customer
            
        if recipient:
            notification, created = ChatNotification.objects.get_or_create(
                user=recipient,
                chat_room=chat_room,
                defaults={'count': 1}
            )
            if not created:
                notification.increment()


class UnreadMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return Message.objects.filter(
            chat_room_id=room_id,
            is_read=False
        ).exclude(sender=self.request.user)


class MarkMessagesAsReadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        messages = Message.objects.filter(
            chat_room_id=room_id,
            is_read=False
        ).exclude(sender=request.user)
        
        # Mark messages as read
        messages.update(is_read=True)
        
        # Clear notification
        ChatNotification.objects.filter(
            user=request.user,
            chat_room_id=room_id
        ).update(count=0)
        
        return Response({'status': 'messages marked as read'})


class ChatNotificationListView(generics.ListAPIView):
    serializer_class = ChatNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatNotification.objects.filter(
            user=self.request.user,
            count__gt=0
        ).select_related('chat_room')
    

class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # Admin sees all chatrooms
            return ChatRoom.objects.all().order_by('-updated_at')
        else:  # Customer sees only their chatrooms
            return ChatRoom.objects.filter(customer=user).order_by('-updated_at')