import json

from ..models_app.models import Conversation,Message,Group
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

@database_sync_to_async
def save_message(conversation_name,writer,message_text,kind_mes="text",url_mes=None):
    conversation=Conversation.objects.get(name=conversation_name)        
    message=Message(conversation=conversation,writer_name=writer,text=message_text,kind=kind_mes,url=url_mes)
    message.save()

@database_sync_to_async
def save_message_group(group_name,writer,text,kind_mes="text",url_mes=None):
    group=Group.objects.get(name=group_name)
    message=Message(group=group,writer_name=writer,text=text,kind=kind_mes,url=url_mes)
    message.save()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_name=self.scope["url_route"]["kwargs"]["conversation_name"]
        self.conversation_group_name=f"chat_{self.conversation_name}"
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        await self.accept()
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )
    async def receive(self, text_data=None, bytes_data=None):
        td=json.loads(text_data)
        message_text=td["message"]
        writer=td["writer"]
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                "type":"chat_message",
                "conversation":str(td["conversation"]),
                "kind":str(td["kind"]),
                "url":td["url"],
                "message":str(message_text),
                "writer":str(writer)
            }
        )
    async def chat_message(self,event):
        message=event["message"]
        writer=event["writer"]
        kind=event["kind"]
        url=None
        if kind!="text":
            url=event["url"]
        await self.send(text_data=json.dumps({
            "message":str(message),
            "writer":str(writer),
            "url":url,
            "kind":kind
        }))
        await save_message(event["conversation"],writer,message,kind,url)
            
class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name=self.scope["url_route"]["kwargs"]["group_name"]
        self.group_group_name=f"chat_{self.group_name}"
        await self.channel_layer.group_add(
            self.group_group_name,
            self.channel_name
        )
        await self.accept()
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_group_name,
            self.channel_name
        )
    async def receive(self, text_data=None, bytes_data=None):
        td=json.loads(text_data)
        message_text=td["message"]
        writer=td["writer"]
        await self.channel_layer.group_send(
            self.group_group_name,
            {
                "type":"chat_message",
                "group":str(td["group"]),
                "kind":str(td["kind"]),
                "url":td["url"],
                "message":str(message_text),
                "writer":str(writer)
            }
        )
    async def chat_message(self,event):
        message=event["message"]
        writer=event["writer"]
        kind=event["kind"]
        url=None
        if kind!="text":
            url=event["url"]
        await self.send(text_data=json.dumps({
            "message":str(message),
            "writer":str(writer),
            "url":url,
            "kind":kind
        }))
        await save_message_group(event["group"],writer,message,kind,url)