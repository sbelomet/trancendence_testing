# users/admin.py

from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Friendship

#  django.contrib pour l'interface d'administration Django.
# création d'un type ce client admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']

#enregistrement de modèles
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Friendship)
