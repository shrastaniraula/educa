import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync,sync_to_async
from django.utils import timezone
from .models import Message
from django.contrib.auth.models import User
import base64
from django.core.files.base import ContentFile
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = f'chat_{self.id}'

        # join room group
        await self.channel_layer.group_add(
        self.room_group_name,
        self.channel_name
        )

        # accept connection
        await self.accept()

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def handle_image_message(self, base64_image_data):
        user_instance = User.objects.get(id=self.user.id)
        
        # Decode the base64 image data
        format, imgstr = base64_image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_data = ContentFile(base64.b64decode(imgstr), name=f'image.{ext}')

        # new_image_message = Message(room=self.room_group_name, user=user_instance, image=message)

        new_image_message = Message(
            room=self.room_group_name,
            user=user_instance,
            image=image_data  # Save the actual image file
        )
        new_image_message.save()

    # receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']  # Get message type or default to 'text'
        print(f"\n\n\n\n{message_type}\n\n\n")
        message = text_data_json['message']

        if message_type == 'text':
            user_instance = await sync_to_async(User.objects.get)(id=self.user.id)
            new_text_message = Message(room= self.room_group_name, user = user_instance , message = message)
            await sync_to_async(new_text_message.save)()
            now = timezone.now()
            await self.channel_layer.group_send(
                # new_message.save()

                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                    'datetime': now.isoformat(),
                }
                
            )

        elif message_type == 'image':
            # Handling image message

            # user_instance = await sync_to_async(User.objects.get)(id=self.user.id)
            # new_image_message = Message(room=self.room_group_name, user=user_instance, image=message)
            # await sync_to_async(new_image_message.save)()


            now = timezone.now()
            await self.channel_layer.group_send(
                # new_message.save()

                self.room_group_name,
                {
                    'type': 'image',
                    'message': message,
                    'user': self.user.username,
                    'datetime': now.isoformat(),
                }
                
            )
            await self.handle_image_message(message)

    # receive message from room group
    async def chat_message(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def image(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps(event))


