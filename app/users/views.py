# users/views.py

from rest_framework import viewsets, permissions, status
from django.contrib.auth import get_user_model
from .models import PlayerStatistics
from .models import Friendship
from .serializers import UserSerializer, FriendshipSerializer, RegisterSerializer, UserPublicSerializer, UserDetailSerializer, UserLoginSerializer, PlayerStatisticsSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.decorators import action
from .permissions import IsFriend, IsOwnerOrAdmin, IsFriendshipRecipientOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView

#select_related permet le lazy loading et récupère la requete SQL en une fois
#plutot que d'itérer dans toute la DB et faire autant de requetes
#Utilisé pour les relations de type ForeignKey et OneToOneField.
#pour les relations  ManyToManyField et ForeignKey inversé il faut utiliser
#prefetch_related qui va attacher chaque requete et renvoyer le resultat final en une fois
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('friends', 'match_history__gameplayer_set__player').all()
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserPublicSerializer
        else:
            return UserSerializer
    #voir les amis d'un ami
    @action(detail=True, methods=['get'], permission_classes=[IsFriend])
    def see_friends(self, request, pk=None):
        user = self.get_object()
        friends = user.friends.prefetch_related('avatar').all()
        serializer = UserPublicSerializer(friends, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def see_online(self, request, pk=None):
        connected = User.objects.filter(is_online=True).exclude(id=request.user.id)
        serializer = UserPublicSerializer(connected, many=True, context={'request': request})
        return Response(serializer.data)

class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh":str(token),
                          "access": str(token.access_token)}
        return Response(data, status= status.HTTP_201_CREATED)
    
class UserLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        user.is_online = True
        user.save()
        serializer = UserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data['tokens'] = {'refresh':str(token),
                          'access': str(token.access_token)}
        return Response(data, status = status.HTTP_200_OK)
    
class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            if refresh_token is None:
                return Response({"detail": "Le token de rafraîchissement est manquant."}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            request.user.is_online = False
            request.user.save(update_fields=['is_online'])
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        
class PlayerStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlayerStatistics.objects.all()
    serializer_class = PlayerStatisticsSerializer

class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.select_related('from_user', 'to_user').all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=True, methods=['put'], permission_classes=[IsFriendshipRecipientOrAdmin])
    def accept_friendship(self, request, pk=None):
        friendship = self.get_object()
        if friendship.is_confirmed:
            return Response({"detail": "Vous êtes déjà amis avec cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)
        friendship.is_confirmed = True
        friendship.created_at = timezone.now()
        friendship.save()
        return Response({"detail": "Demande d'ami acceptée avec succès."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], permission_classes=[IsFriendshipRecipientOrAdmin])
    def refuse_friendship(self, request, pk=None):
        friendship = self.get_object()
        if friendship.is_confirmed:
            return Response({"detail": "Vous êtes déjà amis avec cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)
        friendship.delete()
        return Response({"detail": "Demande d'ami a été refusée par l'utilisateur."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], permission_classes=[IsOwnerOrAdmin])
    def delete_friendship(self, request, pk=None):
        friendship = self.get_object()
        if not friendship.is_confirmed:
            return Response({"detail": "Vous n'êtes pas ami avec cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)
        friendship.is_confirmed = False
        friendship.created_at = None
        return Response({"detail": "Vous avez retiré cet utilisateur de votre liste d'ami."}, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['accept_friendship', 'refuse_friendship']:
            permission_classes = [IsFriendshipRecipientOrAdmin]
        else:
            permission_classes = [IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

""" class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = token.user
        return Response({'token': token.key, 'user_id': user.pk, 'username': user.username}) """
    