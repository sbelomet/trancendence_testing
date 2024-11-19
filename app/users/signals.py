from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import CustomUser

@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    if isinstance(user, CustomUser):
        user.is_online = True
        user.save(update_fields=['is_online'])


@receiver(user_logged_out)
def post_logout(sender, user, request, **kwargs):
    if isinstance(user, CustomUser):
        user.is_online = False
        user.save(update_fields=['is_online'])

