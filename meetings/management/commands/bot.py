from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, Request

class Command(BaseCommand):
    help = 'Telegram-bot'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
            base_url=settings.PROXY_URL
        )
        print(bot.get_me())
