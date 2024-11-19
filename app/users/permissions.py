from rest_framework import permissions
from .models import CustomUser, Friendship

class IsFriend(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Vérifier si l'user(request=> celui qui fait l'action) est authentifié
        if not request.user or not request.user.is_authenticated:
            return False
        #Since friends is a ManyToManyField with a through 
        # relationship, accessing confirmed friendships requires querying 
        # the Friendship model directly to verify if a friendship 
        # exists between the request.user and obj.
        if not isinstance(obj, CustomUser):
            return False
        
        # Renvoyer bool si dans les deux users concernés, la frienship est confirmée
        return Friendship.objects.filter(
            from_user=request.user,
            to_user=obj,
            is_confirmed=True
        ).exists() and Friendship.objects.filter(
            from_user=obj,
            to_user=request.user,
            is_confirmed=True
        ).exists()

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if isinstance(obj, CustomUser): #Pour les objets du CustomUser
            return obj == request.user or request.user.is_superuser
        elif isinstance(obj, Friendship): #pour les objets de la friendship
            return (obj.from_user == request.user or obj.to_user == request.user) or request.user.is_superuser
        else:
            return False

    


