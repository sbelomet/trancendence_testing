# users/tests.py

from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Friendship
from rest_framework.authtoken.models import Token

User = get_user_model()

class CustomUserModelTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='password123', email='user1@a.com')
        self.user2 = User.objects.create_user(username='bob', password='password123', email='user2@a.com')
        self.user3 = User.objects.create_user(username='charlie', password='password123', email='user3@a.com')

    def test_user_creation(self):
        """Test la création des utilisateurs"""
        self.assertEqual(self.user1.username, 'alice')
        self.assertEqual(self.user2.username, 'bob')
        self.assertEqual(self.user3.username, 'charlie')
        self.assertTrue(self.user1.check_password('password123'))
        self.assertTrue(self.user2.check_password('password123'))

    def test_user_str_method(self):
        """Test la méthode __str__ des utilisateurs"""
        self.assertEqual(str(self.user1), 'alice')
        self.assertEqual(str(self.user2), 'bob')

class FriendshipAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='password123', email='user1@a.com')
        self.user2 = User.objects.create_user(username='bob', password='password123', email='user2@a.com')
        self.user3 = User.objects.create_user(username='charlie', password='password123', email='user3@a.com')

        
        # Créer des tokens pour chaque utilisateur
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.token3 = Token.objects.create(user=self.user3)
        
        # Authentifier le client en tant qu'alice
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

    def test_send_friend_request(self):
        """Test l'envoi d'une demande d'amitié"""
        url = reverse('friendship-list')  # Nom standardisé par le router
        data = {'to_user': self.user2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.count(), 1)
        friendship = Friendship.objects.first()
        self.assertEqual(friendship.from_user, self.user1)
        self.assertEqual(friendship.to_user, self.user2)
        self.assertFalse(friendship.is_confirmed)

    def test_confirm_friend_request(self):
        """Test la confirmation d'une demande d'amitié"""
        # Créer une amitié non confirmée
        friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        
        # Authentifier le client en tant que bob pour confirmer l'amitié
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        url = reverse('friendship-detail', args=[friendship.id])
        data = {'is_confirmed': True}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friendship.refresh_from_db()
        self.assertTrue(friendship.is_confirmed)

    def test_prevent_duplicate_friendships(self):
        """Test qu'une amitié dupliquée ne peut pas être créée"""
        # Créer une amitié existante
        Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        
        # Tenter de créer une amitié dupliquée
        url = reverse('friendship-list')
        data = {'to_user': self.user2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Friendship.objects.count(), 1)

    def test_cannot_friend_self(self):
        """Test qu'un utilisateur ne peut pas s'ajouter lui-même comme ami via l'API"""
        url = reverse('friendship-list')
        data = {'to_user': self.user1.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Friendship.objects.count(), 0)


class UserAPITest(APITestCase):
    def test_create_user(self):
        """Test la création d'un utilisateur via l'API"""
        url = reverse('register')
        data = {
            'username': 'david',
            'email': 'david@example.com',
            'password': 'securepassword123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='david')
        self.assertTrue(user.check_password('securepassword123'))
        self.assertNotIn('password', response.data)


class PermissionTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='password123', email='alice@example.com')
        self.user2 = User.objects.create_user(username='bob', password='password123', email='bob@example.com')
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)

    def test_only_friends_can_see_friends(self):
        """Test que seul un ami peut voir les amis d'un utilisateur"""
        # Authentifier en tant que user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        # Tenter de voir les amis de user2 (ils ne sont pas encore amis)
        url = reverse('user-see-friends', args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Créer une amitié confirmée entre user1 et user2
        Friendship.objects.create(from_user=self.user1, to_user=self.user2, is_confirmed=True)
        Friendship.objects.create(from_user=self.user2, to_user=self.user1, is_confirmed=True)
        # Réessayer
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.test import RequestFactory

class UserSignalsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='testuser@example.com')
        self.factory = RequestFactory()

    def test_user_login_updates_is_online(self):
        """Test que l'utilisateur est marqué en ligne après la connexion"""
        self.assertFalse(self.user.is_online)
        # Simuler le signal de connexion
        request = self.factory.post('/api-token-auth/')
        user_logged_in.send(sender=self.user.__class__, request=request, user=self.user)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_online)

    def test_user_logout_updates_is_online(self):
        """Test que l'utilisateur est marqué hors ligne après la déconnexion"""
        self.user.is_online = True
        self.user.save()
        # Simuler le signal de déconnexion
        request = self.factory.post('/logout/')
        user_logged_out.send(sender=self.user.__class__, request=request, user=self.user)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_online)

