from django.urls import path
from .consumers import ChatConsumer,GroupConsumer

websocket_urlpatterns=[
   path('ws/chat/<str:conversation_name>/', ChatConsumer.as_asgi()),
   path('ws/group/<str:group_name>/',GroupConsumer.as_asgi())
]