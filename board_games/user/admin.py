from django.contrib import admin

from .models import TelegramUser, BoardGames


@admin.register(TelegramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nickname', 'avatar',
    )


@admin.register(BoardGames)
class BoardGamesAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'link_to_bgg'
    )
