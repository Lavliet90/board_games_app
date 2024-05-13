import asyncio
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from board_games.meetings.main_bot import bot


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start bot'

    def handle(self, *args, **options):
        try:
            asyncio.run(bot.infinity_polling(logger_level=settings.LOG_LEVEL))
        except Exception as err:
            logger.error(f'Error: {err}')

