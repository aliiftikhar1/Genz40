from rest_framework import serializers
from .models import ChatRoom, Message, ChatNotification
from django.utils.timesince import timesince

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    timestamp = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()
    
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['id', 'timestamp', 'is_read', 'sender']
    
    def get_timestamp(self, obj):
        return timesince(obj.timestamp) + ' ago'
    
    def get_is_own(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.sender


class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True, allow_null=True)
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'room_name', 'updated_at']
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            notification = ChatNotification.objects.filter(
                user=request.user,
                chat_room=obj
            ).first()
            return notification.count if notification else 0
        return 0
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content,
                'timestamp': timesince(last_message.timestamp) + ' ago',
                'sender': last_message.sender.get_full_name()
            }
        return None


class ChatNotificationSerializer(serializers.ModelSerializer):
    chat_room = ChatRoomSerializer(read_only=True)
    
    class Meta:
        model = ChatNotification
        fields = ['id', 'user', 'chat_room', 'count', 'last_updated']
        read_only_fields = ['id', 'last_updated']