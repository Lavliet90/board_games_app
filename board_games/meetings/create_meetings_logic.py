import logging
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
from .models import Meeting
from board_games.user.models import TelegramUser
from .validators import validate_date

logger = logging.getLogger(__name__)


async def handle_start_table(bot, callback_query, states_user):
    await bot.answer_callback_query(callback_query.id)
    telegram_id = callback_query.from_user.id
    nickname = callback_query.from_user.username

    try:
        user = await sync_to_async(TelegramUser.objects.get)(telegram_id=telegram_id)
    except ObjectDoesNotExist:
        user = await sync_to_async(TelegramUser.objects.create)(
            telegram_id=telegram_id, nickname=nickname
        )

    await bot.send_message(
        callback_query.message.chat.id, "Введите название мероприятия:"
    )
    states_user[callback_query.from_user.id] = {"user": user, "step": "title"}


async def process_title_step(bot, message, states_user):
    user = states_user[message.from_user.id]["user"]
    try:
        new_meeting = Meeting()
        new_meeting.creator = user
        new_meeting.title = message.text

        await bot.send_message(message.chat.id, "Введите описание мероприятия:")
        states_user[message.from_user.id] = {
            "meeting": new_meeting,
            "step": "description",
        }
    except Exception as e:
        await bot.reply_to(
            message, "Ошибка при создании мероприятия. Попробуйте еще раз."
        )


async def process_description_step(bot, message, states_user):
    new_meeting = states_user[message.from_user.id]["meeting"]
    try:
        new_meeting.description = message.text

        await bot.send_message(
            message.chat.id, "Введите дату мероприятия (в формате YYYY-MM-DD HH:MM):"
        )
        states_user[message.from_user.id]["step"] = "date"
    except Exception as e:
        await bot.reply_to(
            message, "Ошибка при вводе описания мероприятия. Попробуйте еще раз."
        )


async def process_date_step(bot, message, states_user):
    new_meeting = states_user[message.from_user.id]["meeting"]
    try:
        valid, error_message = validate_date(message.text)
        if valid:
            new_meeting.date = message.text

            await bot.send_message(
                message.chat.id, "Введите максимальное число игроков:"
            )
            states_user[message.from_user.id]["step"] = "max_users"
        else:
            await bot.send_message(message.chat.id, error_message)
    except Exception as e:
        await bot.reply_to(
            message, "Ошибка при вводе даты мероприятия. Попробуйте еще раз."
        )


async def process_max_users_step(bot, message, states_user):
    new_meeting = states_user[message.from_user.id]["meeting"]
    try:
        new_meeting.max_users = int(message.text)
        await sync_to_async(new_meeting.save)()
        await bot.send_message(message.chat.id, "Мероприятие успешно создано!")
        states_user.pop(message.from_user.id)
    except ValueError:
        await bot.reply_to(
            message, "Введите корректное число для максимального числа игроков."
        )
    except Exception as e:
        await bot.reply_to(
            message, "Ошибка при вводе максимального числа игроков. Попробуйте еще раз."
        )
