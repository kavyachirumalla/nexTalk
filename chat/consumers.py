import json
from urllib.parse import unquote
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import  Message, Room
from django.contrib.auth.models import User
class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = unquote(self.scope['url_route']['kwargs']['room_name'])
        safe_room_name=self.room_name.replace(" ", "_")
        self.room_group_name=f"chat_{safe_room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "status": "online",
                "username": self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous"
            }
        )
#user will join a room group when they connect to the websocket
#the group name is based on the room name, so all users in the same room will join the same group
#when a user disconnects from the websocket, they will leave the room group and their status will be broadcasted to the group as offline
    async def disconnect(self, close_code):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_status",
                "status": "offline",
                "username": self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous"
            }
        )
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
#database operations are asynchronous in channels
#database_sync_to_async prevents blocking async websocket flow
    @database_sync_to_async
    def save_message(self, sender_username, content):
        user = User.objects.get(username=sender_username)
        room = Room.objects.get(name=self.room_name)
        msg=Message.objects.create(room=room, sender=user, content=content)
        return msg
#main method to receive messages from the websocket
#delegates events to different handlers based on the type of event
    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type")
        if event_type == "typing":
            await self.handle_typing(data)
        
        elif event_type == "message":
            await self.handle_message(data)
#handler for message events, saves the message to the database and broadcasts it to the group
    async def handle_message(self, data):
        message = data.get("message")
        sender_username = data.get("username")
        saved_message = await self.save_message(sender_username, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "message_event",
                "message": message,
                "username": sender_username,
                "time": timezone.localtime(saved_message.created_at).strftime("%H:%M"),
                "id": saved_message.id,
            }
        )
#handler for typing events, broadcasts the typing status to the group
    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_event",
                "username": data.get("username"),
            }
        )
#send messages payload back to frontend when a message event is received from the group
    async def message_event(self, event):
          await self.send(text_data=json.dumps({
          "message": event["message"],
          "username": event["username"],
          "time": event["time"],
          "id": event["id"],
        }))
    
#send typing status back to frontend when a typing event is received from the group
    async def typing_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"],
        }))
#send online/offline updates to frontend
    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "status",
            "username": event["username"],
            "status": event["status"],
        }))