from django.db import models

from board_games.user.models import User, BoardGames


class Meeting(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='organized_events'
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    date = models.DateTimeField()
    max_users = models.IntegerField()
    board_games = models.ForeignKey(
        BoardGames,
        on_delete=models.CASCADE,
        related_name='list_games_for_party',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title