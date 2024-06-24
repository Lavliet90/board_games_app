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
from .meetings_information import show_me_table_meetings, show_meeting_details, connect_to_meeting

bot = AsyncTeleBot(settings.TOKEN_BOT, parse_mode="HTML")
telebot.logger.setLevel(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)

states_user = {}


@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    text = (
        "Hello. I'm a board game event creation bot. Here is the list of my commands:"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton("Start Table", callback_data="start_table")
    button2 = types.InlineKeyboardButton("Show me meetings", callback_data="show_meetings")
    markup.add(button1, button2)
    await bot.reply_to(message, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "start_table")
async def handle_callback_query(callback_query):
    await handle_start_table(bot, callback_query, states_user)


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


@bot.callback_query_handler(func=lambda call: call.data == "show_meetings")
async def handle_callback_query(callback_query):
    await show_me_table_meetings(bot, callback_query)


@bot.callback_query_handler(func=lambda call: call.data.startswith("meeting_"))
async def handle_meeting_callback_query(callback_query):
    meeting_id = int(callback_query.data.split("_")[-1])
    await show_meeting_details(bot, callback_query, meeting_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("connect_to_meeting_"))
async def handler_connect_to_meeting(callback_query):
    logger.debug('KOK8')
    logging.debug('KOK8')
    meeting_id = int(callback_query.data.split("_")[-1])
    await connect_to_meeting(bot, callback_query, meeting_id)


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if message.chat.type == "private":
        logger.debug(message.from_user)
        # await bot.reply_to(message, message.text)

    elif message.chat.type in ["group", "supergroup"]:
        logger.debug(message.from_user)
        # await bot.reply_to(message, message.text)
