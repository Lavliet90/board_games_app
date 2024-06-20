import logging
from datetime import timezone

import requests

import telebot
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from telebot import types
from telebot.async_telebot import AsyncTeleBot
from .models import Meeting
from board_games.user.models import TelegramUser
from board_games import settings

bot = AsyncTeleBot(settings.TOKEN_BOT, parse_mode='HTML')
telebot.logger.setLevel(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)

states = {}


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    # i like KOK debug for tests
    logger.debug('KOK')
    text = 'Hello. I\'m a board game event creation bot. Here is the list of my commands:'
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Start Table', callback_data='start_table')
    button2 = types.InlineKeyboardButton('Angelina kek', callback_data='kek')
    markup.add(button1, button2)
    await bot.reply_to(message, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'start_table')
async def handle_callback_query(callback_query):
    await bot.answer_callback_query(callback_query.id)
    telegram_id = callback_query.from_user.id
    nickname = callback_query.from_user.username

    try:
        user = await sync_to_async(TelegramUser.objects.get)(telegram_id=telegram_id)
    except ObjectDoesNotExist:
        user = await sync_to_async(TelegramUser.objects.create)(
            telegram_id=telegram_id, nickname=nickname
        )

    await bot.send_message(callback_query.message.chat.id, 'Введите название мероприятия:')
    states[callback_query.from_user.id] = {"user": user, "step": "title"}


@bot.message_handler(
    func=lambda message: message.from_user.id in states and states[message.from_user.id]["step"] == "title")
async def process_title_step(message):
    user = states[message.from_user.id]["user"]
    try:
        new_meeting = Meeting()
        new_meeting.creator = user
        new_meeting.title = message.text

        await bot.send_message(message.chat.id, 'Введите описание мероприятия:')
        states[message.from_user.id] = {"meeting": new_meeting, "step": "description"}
    except Exception as e:
        await bot.reply_to(message, 'Ошибка при создании мероприятия. Попробуйте еще раз.')


@bot.message_handler(
    func=lambda message: message.from_user.id in states and states[message.from_user.id]["step"] == "description")
async def process_description_step(message):
    new_meeting = states[message.from_user.id]["meeting"]
    try:
        new_meeting.description = message.text

        await bot.send_message(message.chat.id, 'Введите дату мероприятия (в формате YYYY-MM-DD HH:MM):')
        states[message.from_user.id]["step"] = "date"
    except Exception as e:
        await bot.reply_to(message, 'Ошибка при вводе описания мероприятия. Попробуйте еще раз.')


@bot.message_handler(
    func=lambda message: message.from_user.id in states and states[message.from_user.id]["step"] == "date")
async def process_date_step(message):
    new_meeting = states[message.from_user.id]["meeting"]
    logger.debug('LOLOLOL')
    logger.debug(message.text)
    logger.debug(timezone.now())
    if message.text < timezone.now():
        await bot.reply_to(message, 'Дата не может быть раньше сегодня.')
    try:
        new_meeting.date = message.text

        await bot.send_message(message.chat.id, 'Введите максимальное число игроков:')
        states[message.from_user.id]["step"] = "max_users"
    except Exception as e:
        await bot.reply_to(message, 'Ошибка при вводе даты мероприятия. Попробуйте еще раз.')


@bot.message_handler(
    func=lambda message: message.from_user.id in states and states[message.from_user.id]["step"] == "max_users")
async def process_max_users_step(message):
    new_meeting = states[message.from_user.id]["meeting"]
    try:
        new_meeting.max_users = int(message.text)
        await sync_to_async(new_meeting.save)()
        await bot.send_message(message.chat.id, 'Мероприятие успешно создано!')
        states.pop(message.from_user.id)
    except ValueError:
        await bot.reply_to(message, 'Введите корректное число для максимального числа игроков.')
    except Exception as e:
        await bot.reply_to(message, 'Ошибка при вводе максимального числа игроков. Попробуйте еще раз.')


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if message.chat.type == 'private':
        logger.debug(message.from_user)
        await bot.reply_to(message, message.text)

    elif message.chat.type in ['group', 'supergroup']:
        logger.debug(message.from_user)
        await bot.reply_to(message, message.text)
