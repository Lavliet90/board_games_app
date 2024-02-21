from django.db import models


class User(models.Model):

    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=70)
    nickname = models.CharField(max_length=20)
    boardgames = models.ManyToManyField('BoardGame', related_name='users')
    friends = models.ManyToManyField('self', related_name='friends', symmetrical=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


class BoardGames(models.Model):

    title = models.CharField(max_length=150)
    link_to_bgg = models.URLField()
    users = models.ManyToManyField(User, related_name='boardgames')
