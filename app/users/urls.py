
# users/urls.py

from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, FriendshipViewSet, RegistrationView, UserLoginView, UserLogoutView
from rest_framework_simplejwt.views import TokenRefreshView


# Un routeur est utilisé en conjonction avec les ViewSets pour générer automatiquement les URL des endpoints de l'API.
# Il mappe les actions des ViewSets aux routes HTTP correspondantes.

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'friendships', FriendshipViewSet, basename='friendship')

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
	path('register/', RegistrationView.as_view(), name='register'),
	path('login/', UserLoginView.as_view(), name='login-user'),
	path('logout/', UserLogoutView.as_view(), name='logout-user'),
    path('', include(router.urls)),
]


