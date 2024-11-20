# server_side_pong/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/server_side_pong/', consumers.PongConsumer.as_asgi()),
]
