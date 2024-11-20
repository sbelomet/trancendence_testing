from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Friendship, PlayerStatistics
from rest_framework.test import APIClient
from server_side_pong.models import Game, GamePlayer
from django.utils import timezone


User = get_user_model()


def authenticate(client, username, password):
    """Authentifie un utilisateur et configure les en-têtes JWT."""
    login_url = reverse('login-user')
    response = client.post(login_url, {'username': username, 'password': password}, format='json')
    #print("Login response data:", response.data)
    assert response.status_code == status.HTTP_200_OK, f"Login failed: {response.data}"
    token = response.data['tokens']['access']  # Récupérer le token JWT
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')



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

        # Authentifier le client en tant qu'alice
        authenticate(self.client, username='alice', password='password123')

    def test_send_friend_request(self):
        """Test l'envoi d'une demande d'amitié"""
        authenticate(self.client, username='alice', password='password123')
        url = reverse('friendship-list')
        data = {'to_user': self.user2.id}
        response = self.client.post(url, data, format='json')
        #print("Response data:", response.data)
        #print("Status code:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.count(), 1)

    def test_confirm_friend_request(self):
        """Test que seul le destinataire peut confirmer une demande d'amitié"""
        # Clients pour chaque utilisateur
        client_alice = APIClient()
        client_bob = APIClient()
        client_charlie = APIClient()

        # Alice envoie une demande d'amitié à Bob
        authenticate(client_alice, username='alice', password='password123')
        url = reverse('friendship-list')
        data = {'to_user': self.user2.id}  # Bob
        response = client_alice.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        friendship = Friendship.objects.get(from_user=self.user1, to_user=self.user2)

        # Alice tente d'accepter la demande (devrait échouer)
        authenticate(client_alice, username='alice', password='password123')
        url = reverse('friendship-accept-friendship', args=[friendship.id])
        response = client_alice.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Bob accepte la demande
        authenticate(client_bob, username='bob', password='password123')
        url = reverse('friendship-accept-friendship', args=[friendship.id])
        response = client_bob.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friendship.refresh_from_db()
        self.assertTrue(friendship.is_confirmed)

        # Charlie tente d'accepter la demande (devrait échouer)
        authenticate(client_charlie, username='charlie', password='password123')
        url = rurl = reverse('friendship-accept-friendship', args=[friendship.id])
        response = client_charlie.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_prevent_duplicate_friendships(self):
        """Test qu'une amitié dupliquée ne peut pas être créée"""
        Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        url = reverse('friendship-list')
        data = {'to_user': self.user2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_friend_self(self):
        """Test qu'un utilisateur ne peut pas s'ajouter lui-même comme ami via l'API"""
        url = reverse('friendship-list')
        data = {'to_user': self.user1.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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

    def test_only_friends_can_see_friends(self):
        """Test que seul un ami peut voir les amis d'un utilisateur"""
        authenticate(self.client, username='alice', password='password123')

        # Tenter de voir les amis de user2 (ils ne sont pas encore amis)
        url = reverse('user-see-friends', args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Créer une amitié confirmée entre user1 et user2
        friendship = Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        authenticate(self.client, username='bob', password='password123')
        url = reverse('friendship-detail', args=[friendship.id])
        data = {'is_confirmed': True}
        response = self.client.patch(url, data, format='json')
        #print("Response data:", response.data)
        #print("Status code:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        friendship.refresh_from_db()
        self.assertTrue(friendship.is_confirmed)
        authenticate(self.client, username='alice', password='password123')
        url = reverse('user-see-friends', args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refuse_friend_request(self):
        """Test que seul le destinataire peut refuser une demande d'amitié"""
        # Clients pour chaque utilisateur
        client_alice = APIClient()
        client_bob = APIClient()

        # Alice envoie une demande d'amitié à Bob
        authenticate(client_alice, username='alice', password='password123')
        url = reverse('friendship-list')
        data = {'to_user': self.user2.id}
        response = client_alice.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        friendship = Friendship.objects.get(from_user=self.user1, to_user=self.user2)

        # Alice tente de refuser la demande (devrait échouer)
        authenticate(client_alice, username='alice', password='password123')
        url = reverse('friendship-refuse-friendship', args=[friendship.id])
        response = client_alice.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Bob refuse la demande
        authenticate(client_bob, username='bob', password='password123')
        url = reverse('friendship-refuse-friendship', args=[friendship.id])
        response = client_bob.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Friendship.objects.filter(id=friendship.id).exists())


class UserSignalsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='testuser@example.com')

    def test_user_login_updates_is_online(self):
        """Test que l'utilisateur est marqué en ligne après la connexion"""
        authenticate(self.client, username='testuser', password='testpassword')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_online)

    def test_user_logout_updates_is_online(self):
        """Test que l'utilisateur est marqué hors ligne après la déconnexion"""
        authenticate(self.client, username='testuser', password='testpassword')
        # Retrieve the refresh token
        login_url = reverse('login-user')
        response = self.client.post(login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        refresh_token = response.data['tokens']['refresh']

        # Perform logout with refresh token
        logout_url = reverse('logout-user')
        response = self.client.post(logout_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_online)


# class MatchHistoryAPITest(APITestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(
#             username='alice', password='password123', email='alice@example.com'
#         )
#         self.user2 = User.objects.create_user(
#             username='bob', password='password123', email='bob@example.com'
#         )
#         self.client1 = APIClient()
#         self.client2 = APIClient()
#         authenticate(self.client1, username='alice', password='password123')
#         authenticate(self.client2, username='bob', password='password123')

#     def test_match_history_update_on_game_creation(self):
#         """Test que le match_history est mis à jour après la création d'un jeu."""
#         # Créer un jeu entre user1 et user2
#         game = Game.objects.create(
#             rounds_needed=3,
#             start_time=timezone.now(),
#             status='completed'
#         )
#         GamePlayer.objects.create(game=game, player=self.user1, score=10)
#         GamePlayer.objects.create(game=game, player=self.user2, score=15)
#         game.winner = self.user2
#         game.end_time = timezone.now()
#         game.save()

#         # Vérifier que le match est dans le match_history de user1
#         self.user1.refresh_from_db()
#         self.assertIn(game, self.user1.match_history.all())

#         # Vérifier que le match est dans le match_history de user2
#         self.user2.refresh_from_db()
#         self.assertIn(game, self.user2.match_history.all())


#     def test_match_history_serialization(self):
#         """Test que le match_history est correctement sérialisé."""
#         # Créer un jeu entre user1 et user2
#         game = Game.objects.create(
#             rounds_needed=5,
#             start_time=timezone.now(),
#             status='completed'
#         )
#         GamePlayer.objects.create(game=game, player=self.user1, score=8)
#         GamePlayer.objects.create(game=game, player=self.user2, score=12)
#         game.winner = self.user2
#         game.end_time = timezone.now()
#         game.save()

#         # Récupérer les détails de user1
#         url = reverse('user-detail', args=[self.user1.id])
#         response = self.client1.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Vérifier que le match_history est présent et contient le jeu
#         match_history = response.data.get('match_history', [])
#         self.assertEqual(len(match_history), 1)
#         self.assertEqual(match_history[0]['id'], game.id)


# class PlayerStatisticsAPITest(APITestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(
#             username='alice', password='password123', email='alice@example.com'
#         )
#         self.user2 = User.objects.create_user(
#             username='bob', password='password123', email='bob@example.com'
#         )
#         self.client1 = APIClient()
#         authenticate(self.client1, username='alice', password='password123')

#     def test_player_statistics_update_on_game_creation(self):
#         """Test que les statistiques sont mises à jour après un jeu."""
#         # Créer un jeu où user1 gagne contre user2
#         game = Game.objects.create(
#             rounds_needed=3,
#             start_time=timezone.now(),
#             status='completed'
#         )
#         GamePlayer.objects.create(game=game, player=self.user1, score=15)
#         GamePlayer.objects.create(game=game, player=self.user2, score=10)
#         game.winner = self.user1
#         game.end_time = timezone.now()
#         game.save()

#         # Mettre à jour les statistiques via le signal
#         # Le signal devrait être automatiquement appelé lors de la création de GamePlayer
#         # Si ce n'est pas le cas, vous pouvez appeler manuellement update_player_statistics
#         # Mais normalement, ce n'est pas nécessaire si le signal est correctement connecté

#         # Vérifier les statistiques de user1
#         stats = PlayerStatistics.objects.get(player=self.user1)
#         self.assertEqual(stats.matches_played, 1)
#         self.assertEqual(stats.matches_won, 1)
#         self.assertEqual(stats.total_points, 15)
#         self.assertEqual(stats.win_rate, 100)
#         self.assertEqual(stats.average_score, 15)


#     def test_player_statistics_serialization(self):
#         """Test que les statistiques sont correctement sérialisées."""
#         # Créer des statistiques pour user1
#         PlayerStatistics.objects.create(
#             player=self.user1, matches_played=5, matches_won=3, total_points=50
#         )

#         # Récupérer les détails de user1
#         url = reverse('user-detail', args=[self.user1.id])
#         response = self.client1.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Vérifier que les statistiques sont présentes et correctes
#         stats = response.data.get('stats', {})
#         self.assertEqual(stats['matches_played'], 5)
#         self.assertEqual(stats['matches_won'], 3)
#         self.assertEqual(stats['total_points'], 50)
#         self.assertEqual(stats['win_rate'], 60.0)
#         self.assertEqual(stats['average_score'], 10.0)

