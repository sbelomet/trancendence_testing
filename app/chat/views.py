from django.shortcuts import render
from django.http import JsonResponse

from .models import Message


def index(request):
	return render(request, "chat/index.html")

def room(request, room_name):
	username = request.GET.get('username', 'Anomymous')
	messages = Message.objects.filter(room=room_name)[0:25]

	return render(request, "chat/room.html", {"room_name": room_name, 'username': username, 'messages': messages})

def get_message(request, room_name):
	print("fetching last message")
	message = Message.objects.filter(room=room_name).last()
	return JsonResponse({'username': message.username, 'message': message.content})