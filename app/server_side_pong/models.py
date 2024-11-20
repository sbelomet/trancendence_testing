from django.db import models
from users.models import PlayerStatistics

# Create your models here.

# Games Model
class Game(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'), # 'ongoing' is stored in the database, 'Ongoing' is displayed
        ('completed', 'Completed'), # 'completed' is stored in the database, 'Completed' is displayed
    ]

    rounds_needed = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    winner = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='games_won')

    def __str__(self):
        return f"Game {self.id} - {self.status}"

# GamePlayers Model
class GamePlayer(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)  # Assuming you have a Player model in a 'players' app
    score = models.IntegerField(default=0)
    position = models.IntegerField()

    def __str__(self):
        return f"Player {self.player.id} in Game {self.game.id}"
