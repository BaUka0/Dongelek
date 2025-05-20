import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.db.models import Q
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Check if user has access to this conversation
        if not self.user.is_authenticated:
            await self.close()
            return

        has_access = await self.has_conversation_access()
        if not has_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            
            if 'message' in text_data_json:
                message_content = text_data_json['message'].strip()
                
                if not message_content:
                    return
                
                # Save message to database
                message = await self.save_message(message_content)
                
                # Get other user for notification
                other_user = await self.get_other_user()
                conversation = await self.get_conversation()
                
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message_id': message.id,
                        'message': message_content,
                        'sender_id': self.user.id,
                        'sender_name': self.user.username,
                        'timestamp': message.created_at.strftime('%H:%M')
                    }
                )
                
                # Send notification to other user
                notification_group = f'notifications_{other_user.id}'
                await self.channel_layer.group_send(
                    notification_group,
                    {
                        'type': 'notification_message',
                        'message': message_content,
                        'sender_name': self.user.username,
                        'sender_id': self.user.id,
                        'conversation_id': self.conversation_id,
                        'unread_count': await self.get_unread_count(other_user),
                        'car_details': await self.get_car_details(conversation)
                    }
                )
            elif 'typing' in text_data_json:
                typing_status = text_data_json['typing']
                
                # Send typing status to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_status',
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'typing': typing_status
                    }
                )
        except Exception as e:
            print(f"Error processing message: {e}")

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message_id': event['message_id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp']
        }))

    # Receive typing status from room group
    async def typing_status(self, event):
        # Send typing status to WebSocket
        await self.send(text_data=json.dumps({
            'typing': event['typing'],
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    @database_sync_to_async
    def get_other_user(self):
        conversation = Conversation.objects.get(id=self.conversation_id)
        return conversation.buyer if conversation.seller == self.user else conversation.seller

    @database_sync_to_async
    def get_unread_count(self, user):
        return Message.objects.filter(
            conversation__in=Conversation.objects.filter(
                Q(buyer=user) | Q(seller=user)
            ),
            is_read=False
        ).exclude(sender=user).count()

    @database_sync_to_async
    def get_conversation(self):
        return Conversation.objects.get(id=self.conversation_id)
        
    @database_sync_to_async
    def get_car_details(self, conversation):
        car = conversation.car
        return {
            'make': car.make,
            'model': car.model,
            'year': car.year,
            'price': str(car.price)
        }

    @database_sync_to_async
    def has_conversation_access(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.buyer == self.user or conversation.seller == self.user
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content
        )

        # Update conversation timestamp
        conversation.updated_at = timezone.now()
        conversation.save()

        return message


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        self.notification_group_name = f'notifications_{self.user.id}'

        # Join notification group
        try:
            await self.channel_layer.group_add(
                self.notification_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"Successfully connected to notification group: {self.notification_group_name}")
        except Exception as e:
            print(f"Error connecting to notification group: {e}")
            # Still accept the connection even if Redis fails
            await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'notification_group_name'):
            try:
                # Leave notification group
                await self.channel_layer.group_discard(
                    self.notification_group_name,
                    self.channel_name
                )
                print(f"Successfully disconnected from notification group: {self.notification_group_name}")
            except Exception as e:
                print(f"Error disconnecting from notification group: {e}")

    # Receive notification from group
    async def notification_message(self, event):
        # Send notification to WebSocket
        try:
            await self.send(text_data=json.dumps({
                'type': 'new_message',
                'message': event.get('message', ''),
                'sender_name': event.get('sender_name', ''),
                'sender_id': event.get('sender_id', ''),
                'conversation_id': event.get('conversation_id', ''),
                'unread_count': event.get('unread_count', 0),
                'car_details': event.get('car_details', {})
            }))
        except Exception as e:
            print(f"Error sending notification: {e}")