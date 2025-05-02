from django.urls import path
from . import views
from chat import consumers

urlpatterns = [
    # Chat room endpoints
    path('rooms/', views.ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    
    # Message endpoints
    path('rooms/list/', views.ChatRoomListView.as_view(), name='chatroom-list'),
    path('rooms/<int:room_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('rooms/<int:room_id>/unread/', views.UnreadMessagesView.as_view(), name='unread-messages'),
    path('rooms/<int:room_id>/read/', views.MarkMessagesAsReadView.as_view(), name='mark-read'),
    
    # Notification endpoints
    path('notifications/', views.ChatNotificationListView.as_view(), name='notification-list'),
]

# WebSocket URL patterns (for Channels)
websocket_urlpatterns = [
    path('ws/chat/<int:room_id>/', consumers.ChatConsumer.as_asgi()),
]