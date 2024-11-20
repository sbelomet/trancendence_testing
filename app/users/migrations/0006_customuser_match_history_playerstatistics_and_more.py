# Generated by Django 5.1.3 on 2024-11-19 15:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_side_pong', '0002_game_winner'),
        ('users', '0005_rename_online_status_customuser_is_online'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='match_history',
            field=models.ManyToManyField(related_name='played_in', through='server_side_pong.GamePlayer', to='server_side_pong.game'),
        ),
        migrations.CreateModel(
            name='PlayerStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matches_played', models.PositiveIntegerField(default=0)),
                ('matches_won', models.PositiveIntegerField(default=0)),
                ('total_points', models.PositiveIntegerField(default=0)),
                ('player', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='stats',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to='users.playerstatistics'),
        ),
    ]