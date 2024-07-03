import logging
import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from board_games import settings
from .create_meetings_logic import (
    handle_start_table,
    process_title_step,
    process_description_step,
    process_date_step,
    process_max_users_step, process_location_step,
)
from .meetings_information import show_me_table_meetings, show_meeting_details, connect_to_meeting, leave_in_meeting, \
    event_type_information, handle_get_me_list_event, delete_event

bot = AsyncTeleBot(settings.TOKEN_BOT, parse_mode="HTML")
telebot.logger.setLevel(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)

states_user = {}


@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    text = (
        "Привет, я бот по созданию и поиску мероприятий, "
        "какие мероприятия тебя интересуют?"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key, value in settings.EVENT_TYPE.items():
        button = types.InlineKeyboardButton(
            key,
            callback_data=f'type_event_{key}'
        )
        markup.add(button)
    markup.add(
        types.InlineKeyboardButton(
            'Показать мои мероприятия',
            callback_data='get_me_list_event'
        )
    )

    await bot.reply_to(message, text, reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('type_event_')
)
async def handler_event_type_information(callback_query):
    event_name = str(callback_query.data.split('_')[-1])
    await event_type_information(bot, callback_query, event_name)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("show_meetings_")
)
async def handle_callback_query(callback_query):
    event_name = str(callback_query.data.split('_')[-1])
    await show_me_table_meetings(bot, callback_query, event_name)


@bot.callback_query_handler(func=lambda call: call.data == 'get_me_list_event')
async def handle_get_me_list_event_callback(callback_query):
    await handle_get_me_list_event(bot, callback_query)

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("start_table_")
)
async def handle_callback_query(callback_query):
    event_name = str(callback_query.data.split('_')[-1])
    if event_name in settings.EVENT_TYPE:
        event_type = event_name
    else:
        event_type = "other"
    states_user[callback_query.from_user.id] = {"event_type": event_type}
    await handle_start_table(bot, callback_query, states_user)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('delete_meeting_')
)
async def handle_delete_meeting(callback_query):
    meeting_id = int(callback_query.data.split("_")[-1])
    await delete_event(bot, callback_query, meeting_id)



@bot.message_handler(
    func=lambda message: message.from_user.id in states_user
    and states_user[message.from_user.id]["step"] == "title"
)
async def process_title_step_wrapper(message):
    await process_title_step(bot, message, states_user)


@bot.message_handler(
    func=lambda message: message.from_user.id in states_user
    and states_user[message.from_user.id]["step"] == "description"
)
async def process_description_step_wrapper(message):
    await process_description_step(bot, message, states_user)


@bot.message_handler(
    func=lambda message: message.from_user.id in states_user
    and states_user[message.from_user.id]["step"] == "date"
)
async def process_date_step_wrapper(message):
    await process_date_step(bot, message, states_user)


@bot.message_handler(
    func=lambda message: message.from_user.id in states_user
    and states_user[message.from_user.id]["step"] == "max_users"
)
async def process_max_users_step_wrapper(message):
    await process_max_users_step(bot, message, states_user)


@bot.message_handler(
    func=lambda message: message.from_user.id in states_user
    and states_user[message.from_user.id]["step"] == "location"
)
async def process_location_step_wrapper(message):
    await process_location_step(bot, message, states_user)




@bot.callback_query_handler(func=lambda call: call.data.startswith("meeting_"))
async def handle_meeting_callback_query(callback_query):
    meeting_id = int(callback_query.data.split("_")[-1])
    await show_meeting_details(bot, callback_query, meeting_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("connect_to_meeting_")
)
async def handler_connect_to_meeting(callback_query):
    meeting_id = int(callback_query.data.split("_")[-1])
    await connect_to_meeting(bot, callback_query, meeting_id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("leave_in_meeting_")
)
async def handler_leave_in_meeting(callback_query):
    meeting_id = int(callback_query.data.split("_")[-1])
    await leave_in_meeting(bot, callback_query, meeting_id)



@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if message.chat.type == "private":
        logger.debug(message.from_user)
        # await bot.reply_to(message, message.text)

    elif message.chat.type in ["group", "supergroup"]:
        logger.debug(message.from_user)
        # await bot.reply_to(message, message.text)
