from django.db import models
from users.models import CustomUser

class Image(models.Model):
	file = models.ImageField(upload_to='avatar/', height_field=None, width_field=None, max_length=100)
	name = models.CharField(max_length=200, unique=True)
	owner = models.ForeignKey(CustomUser,  on_delete=models.CASCADE, related_name="images", null=True, blank=True)
	date = models.DateTimeField(auto_now_add=True)


