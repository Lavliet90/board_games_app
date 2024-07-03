import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from asgiref.sync import sync_to_async
from telebot import types

from .models import Meeting
from ..user.models import TelegramUser
from ..user.user_verification import user_verification

logger = logging.getLogger(__name__)


async def event_type_information(bot, callback_query, event_name):
    await bot.answer_callback_query(callback_query.id)

    text = (
        f"Вы выбрали мероприятия связанные с {event_name}. "
        f"Выберите, что вас интересует дальше"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton(
        "Создать новое мероприятие",
        callback_data=f"start_table_{event_name}"
    )
    button2 = types.InlineKeyboardButton(
        "Покажи уже существующие мероприятия",
        callback_data=f"show_meetings_{event_name}"
    )
    markup.add(button1, button2)

    await bot.send_message(
        callback_query.message.chat.id,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


async def show_me_table_meetings(bot, callback_query, event_name):
    await bot.answer_callback_query(callback_query.id)
    now = timezone.now()

    queryset = Meeting.objects.filter(event_type=event_name, date__gt=now).order_by('-date')
    meetings = await sync_to_async(list)(queryset)

    if meetings:
        message_text = "\n".join(
            [
                f"{i + 1}."
                f"<b>{meeting.title}</b> "
                f"- @{await sync_to_async(lambda: meeting.creator.nickname)()} "
                f"- <i>{meeting.date.strftime('%Y-%m-%d %H:%M')}</i>"
                for i, meeting in enumerate(meetings)
            ]
        )
        markup = types.InlineKeyboardMarkup(row_width=5)
        buttons = []
        for i, meeting in enumerate(meetings):
            button = types.InlineKeyboardButton(
                text=str(i + 1),
                callback_data=f"meeting_{meeting.id}"
            )
            buttons.append(button)

            if len(buttons) == 5:
                markup.add(*buttons)
                buttons = []
        if buttons:
            markup.add(*buttons)

    else:
        message_text = "На данный момент нет запланированных мероприятий."
        markup = None

    await bot.send_message(
        callback_query.message.chat.id,
        f"<strong>Список мероприятий:</strong>\n\n{message_text}\n\n"
        f"Выберите номер мероприятия:",
        reply_markup=markup,
        parse_mode="HTML"
    )


async def show_meeting_details(bot, callback_query, meeting_id):
    await bot.answer_callback_query(callback_query.id)
    meeting = await sync_to_async(Meeting.objects.get)(id=meeting_id)
    players = await sync_to_async(list)(meeting.players.all())
    meeting_details = (
        f"<strong>{meeting.title}</strong>\n"
        f"Организатор: @{await sync_to_async(lambda: meeting.creator.nickname)()}\n"
        f"Дата: {meeting.date.strftime('%Y-%m-%d %H:%M')}\n"
        f"Локация: {meeting.location}\n"
        f"Описание: {meeting.description}\n"
        f"Участники: {', '.join(
            [
                await sync_to_async(lambda user: user.nickname)(user)
                for user in players
            ]
        )}"
    )
    markup = types.InlineKeyboardMarkup()

    user = await user_verification(callback_query)
    if await sync_to_async(meeting.players.filter(id=user.id).exists)():
        button = types.InlineKeyboardButton(
            'Выйти из ивента',
            callback_data=f'leave_in_meeting_{meeting_id}'
        )
    else:
        button = types.InlineKeyboardButton(
            'Присоедениться к ивенту',
            callback_data=f'connect_to_meeting_{meeting_id}'
        )

    if await sync_to_async(lambda: meeting.creator.id == user.id)():
        button_delete_event = types.InlineKeyboardButton(
            'Удалить ивент',
            callback_data=f'delete_meeting_{meeting_id}'
        )
        markup.add(button_delete_event)
    markup.add(button)
    await bot.send_message(
        callback_query.message.chat.id,
        meeting_details,
        reply_markup=markup,
        parse_mode="HTML"
    )


async def connect_to_meeting(bot, callback_query, meeting_id):
    await bot.answer_callback_query(callback_query.id)
    try:
        meeting = await sync_to_async(Meeting.objects.get)(id=meeting_id)
    except ObjectDoesNotExist:
        await bot.send_message(
            callback_query.message.chat.id,
            'Ивента не существует.',
        )
        return
    user = await user_verification(callback_query)

    if await sync_to_async(meeting.players.filter(id=user.id).exists)():
        await bot.send_message(
            callback_query.message.chat.id,
            f'@{user.nickname} уже в группе "{meeting.title}".'
        )
    else:

        await sync_to_async(meeting.players.add)(user)
        await bot.send_message(
            callback_query.message.chat.id,
            f'@{user.nickname} присоеденился(aсь) к группе "{meeting.title}"'
        )


async def leave_in_meeting(bot, callback_query, meeting_id):
    await bot.answer_callback_query(callback_query.id)
    meeting = await sync_to_async(Meeting.objects.get)(id=meeting_id)
    user = await user_verification(callback_query)
    await sync_to_async(meeting.players.remove)(user)
    await bot.send_message(
        callback_query.message.chat.id,
        f'@{user.nickname} вышел(шла) из группы "{meeting.title}"'
    )


async def delete_event(bot, callback_query, meeting_id):
    await bot.answer_callback_query(callback_query.id)
    meeting = await sync_to_async(
        Meeting.objects.select_related('creator').get
    )(id=meeting_id)
    user = await user_verification(callback_query)
    if user.id == meeting.creator.id:
        await sync_to_async(meeting.delete)()
        await bot.send_message(
            callback_query.message.chat.id,
            'Ивент успешно удален.',
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            callback_query.message.chat.id,
            "Вы не можете удалить эту встречу, так как вы не являетесь её создателем.",
            parse_mode="HTML"
        )


#
# async def handle_get_me_list_event(bot, callback_query):
#     await bot.answer_callback_query(callback_query.id)
#     user_id = callback_query.from_user.id
#     try:
#         user = await  sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
#     except:
#
#         logger.debug('KOK')
#     logger.debug(bot)
#     logger.debug(callback_query)


async def handle_get_me_list_event(bot, callback_query):
    await bot.answer_callback_query(callback_query.id)

    user_id = callback_query.from_user.id

    try:
        user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)

        organized_events = await sync_to_async(list)(
            user.organized_events.all().order_by('-date')
        )
        participant_events = await sync_to_async(list)(
            user.meeting_set.filter(~Q(creator=user)).order_by('-date')
        )

        markup = types.InlineKeyboardMarkup(row_width=5)

        number_of_events = 0
        organized_message = \
            f"<strong>Мероприятия созданные вами:</strong>\n\n"

        buttons = []
        if organized_events:
            for meeting in organized_events:
                number_of_events += 1
                event_text = \
                    f"{number_of_events}. <b>{meeting.title}</b> - {meeting.date.strftime('%Y-%m-%d %H:%M')}\n"
                button = types.InlineKeyboardButton(
                    f'{number_of_events}',
                    callback_data=f'meeting_{meeting.id}')
                buttons.append(button)
                organized_message += event_text
        else:
            organized_message = "У вас пока нет организованных мероприятий.\n\n"

        participant_message = \
            f"\n<strong>Чужие мероприятия, в которых вы участник:</strong>\n\n"
        if participant_events:
            for meeting in participant_events:
                number_of_events += 1
                event_text = \
                    f"{number_of_events}. <b>{meeting.title}</b> - {meeting.date.strftime('%Y-%m-%d %H:%M')}"
                button = types.InlineKeyboardButton(
                    f'{number_of_events}',
                    callback_data=f'meeting_{meeting.id}')
                buttons.append(button)
                participant_message += event_text


        else:
            participant_message = "Вы не являетесь участником мероприятий."

        if buttons:
            markup.add(*buttons)
        update_meeting_text = '\n\nВыберите мепроприятие:'
        full_message = organized_message + participant_message + update_meeting_text
        logger.debug('KOK')
        await bot.send_message(
            callback_query.message.chat.id,
            full_message,
            reply_markup=markup,
            parse_mode="HTML"
        )

    except TelegramUser.DoesNotExist:
        await bot.send_message(
            callback_query.message.chat.id,
            "Пользователь не найден."
        )
