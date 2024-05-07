from django.db import models


class User(models.Model):

    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=70)
    nickname = models.CharField(max_length=20)
    boardgames = models.ManyToManyField('BoardGames', related_name='users_users', blank=True)
    friends = models.ManyToManyField('self', related_name='user_friends', symmetrical=False, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.nickname


class BoardGames(models.Model):

    title = models.CharField(max_length=150)
    link_to_bgg = models.URLField()

    def __str__(self):
        return self.title
