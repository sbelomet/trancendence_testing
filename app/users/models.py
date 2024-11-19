from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

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
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return self.username


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

