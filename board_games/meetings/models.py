import logging
from datetime import timezone

from django.core.exceptions import ValidationError
from django.db import models

from board_games.user.models import TelegramUser, BoardGames


class Meeting(models.Model):
    creator = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name='organized_events'
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    date = models.DateTimeField()
    max_users = models.PositiveIntegerField()
    board_games = models.ForeignKey(
        BoardGames,
        on_delete=models.CASCADE,
        related_name='list_games_for_party',
        blank=True,
        null=True
    )

    # def clean(self):
    #     logging.debug('ROR')
    #     logging.debug(self.date)
    #     logging.debug(timezone.now())
    #     if self.date < timezone.now():
    #         raise ValidationError('Дата мероприятия должна быть в будущем.')
    #
    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.title