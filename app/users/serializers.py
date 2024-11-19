# users/serializers.py

from rest_framework import serializers
from .models import CustomUser, Friendship
from upload.models import Image
from django.conf import settings
from .permissions import IsFriend, IsOwnerOrAdmin
from django.contrib.auth import authenticate

# rest_framework (DRF) is a powerful toolkit for building Web APIs with Django.
# An API (Application Programming Interface) allows communication between software applications.
# A RESTful API follows the REST architectural style, using standard HTTP methods.

#la classe Meta dans un serializer sert de validator, pour s'assurer
#que le model est le bon est les données correspondent bien
#et il converti les données en format JSON ou XML 
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_online = serializers.BooleanField(read_only=True)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'avatar', 'is_online']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash le mot de passe
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None) #control mdp géré dans settings
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'avatar', 'is_online']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'avatar']

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return value
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà pris.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)  # Hash le mot de passe
        user.save()
        return user
    
class CustomUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = CustomUser
		fields =('id', 'username', 'email')
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect credentials!')

class FriendshipSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'created_at', 'is_confirmed']
        read_only_fields = ['from_user', 'created_at']
    
    def validate_to_user(self, value):
        user = self.context['request'].user
        if value == user:
            raise serializers.ValidationError("Un utilisateur ne peut pas s'ajouter lui-même comme ami.")
        if Friendship.objects.filter(from_user=user, to_user=value).exists():
            raise serializers.ValidationError("Vous avez déjà envoyé une demande d'amitié à cet utilisateur.")
        return value
    
    def validate(self, data):
        user = self.context['request'].user
        to_user = data.get('to_user')
        # Vérifier que la relation n'est pas déjà confirmée
        if Friendship.objects.filter(from_user=user, to_user=to_user, is_confirmed=True).exists():
            raise serializers.ValidationError("Vous êtes déjà ami avec cet utilisateur.")
        return data
        


