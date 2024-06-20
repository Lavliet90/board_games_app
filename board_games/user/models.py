from django.db import models
from django.utils.translation import gettext as _


class TelegramUser(models.Model):
    telegram_id = models.PositiveBigIntegerField(db_index=True, unique=True)
    name = models.CharField(_('Имя'), max_length=50, blank=True, null=True)
    surname = models.CharField(_('Фамилия'), max_length=70, blank=True, null=True)
    nickname = models.CharField(_('Логин'), max_length=20)
    boardgames = models.ManyToManyField('BoardGames', related_name='users_users', blank=True)
    friends = models.ManyToManyField('self', related_name='user_friends', symmetrical=False, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.nickname


class BoardGames(models.Model):

    title = models.CharField(max_length=150)
    link_to_bgg = models.URLField()
    link_to_rule = models.URLField()

    def __str__(self):
        return self.title
