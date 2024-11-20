# users/serializers.py

from rest_framework import serializers
from .models import CustomUser, Friendship, PlayerStatistics
from upload.models import Image
from django.conf import settings
from .permissions import IsFriend, IsOwnerOrAdmin
from django.contrib.auth import authenticate
from server_side_pong.serializers import GameSerializer

#la classe Meta dans un serializer sert de validator, pour s'assurer
#que le model est le bon est les données correspondent bien
#et il converti les données en format JSON ou XML 
class UserBaseSerializer(serializers.ModelSerializer):
    #password = serializers.CharField(write_only=True)
    is_online = serializers.BooleanField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id','username', 'email', 'avatar', 'is_online']

class UserSerializer(UserBaseSerializer):
    password = serializers.CharField(write_only=True)
    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ['password']
    
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

class UserPublicSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = ['username', 'avatar', 'is_online', 'match_history']
        read_only_fields = fields

class PlayerStatisticsSerializer(serializers.ModelSerializer):
    matches_played = serializers.IntegerField(read_only=True)
    matches_won = serializers.IntegerField(read_only=True)
    total_points = serializers.IntegerField(read_only=True)
    matches_won = serializers.IntegerField(read_only=True)
    total_points = serializers.IntegerField(read_only=True)
    win_rate = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()

    class Meta:
        model = PlayerStatistics
        fields = ['matches_played', 'matches_won', 'total_points', 'win_rate', 'average_score']
    
    def get_win_rate(self, obj):
        return obj.win_rate
    
    def get_average_score(self, obj):
        return obj.average_score
        
class UserDetailSerializer(UserBaseSerializer):
    friends = UserPublicSerializer(many=True)
    stats = PlayerStatisticsSerializer(many=False)
    match_history = GameSerializer(many=True)

    class Meta:
        fields = UserBaseSerializer.Meta.fields + ['friends', 'match_history', 'stats']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    id = serializers.IntegerField(read_only=True)
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


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Utilisateur désactivé.')
                return user
            else:
                raise serializers.ValidationError('Identifiants incorrects.')
        else:
            raise serializers.ValidationError('Veuillez fournir un nom d\'utilisateur et un mot de passe.')


class FriendshipSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'created_at', 'is_confirmed']
        read_only_fields = ['from_user', 'created_at']
    
    def validate_to_user(self, value):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Vous devez être authentifié pour envoyer une demande d'ami.")
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
        


