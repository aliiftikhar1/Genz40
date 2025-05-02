from django.db import models
from backend.models import CustomUser
from django.utils import timezone

class ChatRoom(models.Model):
    """
    Represents a chat room between a customer and admin/staff
    """
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_chatrooms')
    admin = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    subject = models.CharField(max_length=255, default='reservation')
    room_name = models.CharField(max_length=255, unique=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['customer', 'admin']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Chat between {self.customer} and {self.admin or 'unassigned admin'}"
    
    def update_timestamp(self):
        """Update the updated_at field"""
        self.updated_at = timezone.now()
        self.save(update_fields=['updated_at'])


class Message(models.Model):
    """
    Represents a message in the chat room
    """
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['chat_room', 'is_read']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}"
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


class ChatNotification(models.Model):
    """
    Tracks unread messages for users
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'chat_room')
        indexes = [
            models.Index(fields=['user', 'chat_room']),
        ]
    
    def __str__(self):
        return f"{self.count} unread for {self.user}"
    
    def increment(self):
        """Increment unread count"""
        self.count += 1
        self.save(update_fields=['count', 'last_updated'])
    
    def reset(self):
        """Reset unread count to zero"""
        if self.count > 0:
            self.count = 0
            self.save(update_fields=['count', 'last_updated'])