from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PlayerStatistics
from server_side_pong.models import GamePlayer

@receiver(post_save, sender=GamePlayer)
def update_player_statistics(sender, instance, created, **kwargs):
    if created:
        #The underscore (_) is used as a placeholder for the second value returned by 
		# get_or_create, which is created. It's a Python convention to indicate that the value 
		# is intentionally ignored because it’s not needed.
        player_stats, _ = PlayerStatistics.objects.get_or_create(player=instance.player)
        player_stats.matches_played += 1
        player_stats.total_points += instance.score
        if instance.game.winner == instance.player:
            player_stats.matches_won += 1
        player_stats.save()
