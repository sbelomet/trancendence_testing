from django.urls import path, include
from ChitChat.consumer import ChatConsumer


websocket_urlpatterns = [
	path("ws/", ChatConsumer.as_asgi()),
]