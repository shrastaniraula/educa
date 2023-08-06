import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync,sync_to_async
from django.utils import timezone
from .models import Message
from django.contrib.auth.models import User

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

    # receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print(f"\n\n\n\n {message}\n\n\n")
        print(f"\n\n\n\n {self.room_group_name}\n\n\n")
        print(self.user.id)
        user_instance = await sync_to_async(User.objects.get)(id=self.user.id)


        new_message = Message(room= self.room_group_name, user = user_instance , message = message)
        await sync_to_async(new_message.save)()

        # Message.objects.create(room= self.room_group_name, user = self.user.id , message= message)
        
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
        # send message to WebSocket
        # self.send(text_data=json.dumps({'message': message}))


    # receive message from room group
    async def chat_message(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps(event))

