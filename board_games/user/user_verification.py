from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from board_games.user.models import TelegramUser


async def user_verification(callback_query):
    user_info = callback_query.from_user
    try:
        user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_info.id)
    except ObjectDoesNotExist:
        if user_info.nickname:
            user = await sync_to_async(TelegramUser.objects.create)(
                telegram_id=user_info.id, nickname=user_info.nickname
            )
        else:
            user = await sync_to_async(TelegramUser.objects.create)(
                telegram_id=user_info.id, nickname='Пока незнакомец'
            )
    return user