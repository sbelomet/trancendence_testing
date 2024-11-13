from django.shortcuts import render
from django.http import JsonResponse

from .models import Message


def index(request):
	return render(request, "chat/index.html")

def room(request, room_name):
	username = request.GET.get('username', 'Anomymous')
	messages = Message.objects.filter(room=room_name)[0:25]

	return render(request, "chat/room.html", {"room_name": room_name, 'username': username, 'messages': messages})

#def get_messages(request, room_name):
#	messages = Message.objects.filter(room=room_name)[0:25]
#	messages_list = [{'username': msg.username, 'message': msg.content} for msg in messages]
#	return JsonResponse({'messages': messages_list})