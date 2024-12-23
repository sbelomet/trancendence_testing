from django.urls import path

from . import views


urlpatterns = [
	path("", views.index, name="index"),
	path("<str:room_name>/", views.room, name="room"),
	path("messages/<str:room_name>/", views.get_message, name="get_message"),
]