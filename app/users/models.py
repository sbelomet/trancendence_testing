from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum, Q

#les modèles construisent les tables de la DB et
#définit la structure des données (champs, types de données, contraintes) et les comportements associés
#heriter de AbstractUser pour utiliser le modèle user de django
class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email =  models.EmailField(max_length=150, unique=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    friends = models.ManyToManyField(
        'self',
        through='Friendship',
        symmetrical=False,
        related_name='friends_of'
    )
    match_history = models.ManyToManyField(
        'server_side_pong.Game',
        through='server_side_pong.GamePlayer',
        related_name='played_in'
    )
    is_online = models.BooleanField(default=False)
    stats = models.OneToOneField('PlayerStatistics', on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    
    def __str__(self):
        return self.username

#The @property decorator in Python allows you to define methods in a class that
# can be accessed like attributes. This is particularly useful when you want to
# compute a value dynamically based on other fields in the class without storing
# it directly in the database.
class PlayerStatistics(models.Model):
    player = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='statistics')
    matches_played = models.PositiveIntegerField(default=0)
    matches_won = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player.username} Statistics"

    @property
    def win_rate(self):
        return (self.matches_won / self.matches_played) * 100 if self.matches_played > 0 else 0

    @property
    def average_score(self):
        return self.total_points / self.matches_played if self.matches_played > 0 else 0


User = get_user_model()

class Friendship(models.Model):
    from_user = models.ForeignKey(
        User, 
        related_name='friendships_sent', 
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User, 
        related_name='friendships_received', 
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='unique_friendship')
        ]

    def __str__(self):
        return f"{self.from_user.username} is friends with {self.to_user.username}"

    #Valide que from_user et to_user ne sont pas la même personne
    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("Un utilisateur ne peut pas s'ajouter lui-même comme ami.")
#app le clean er enregistre
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

