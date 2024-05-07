import asyncio

from django.core.management.base import BaseCommand

from board_games.meetings.main_bot import bot


class Command(BaseCommand):
    help = "Start bot"

    def handle(self, *args, **options):
        asyncio.run(bot.polling())