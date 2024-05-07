from django.contrib import admin

from .models import User, BoardGames


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'surname', 'nickname', 'avatar',
    )


@admin.register(BoardGames)
class BoardGamesAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'link_to_bgg'
    )
