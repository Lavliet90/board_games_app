import logging

import telebot
from telebot.async_telebot import AsyncTeleBot

from board_games import settings

bot = AsyncTeleBot(settings.TOKEN_BOT, parse_mode='HTML')
telebot.logger.setLevel(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)

@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    # i like KOK debug for tests
    logger.debug('KOK')
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if message.chat.type == 'private':
        logger.debug('KOK')
        logger.debug(message)
        logger.debug(message.from_user)
        logger.debug('KOK2')
        await bot.reply_to(message, message.text)
    elif message.chat.type in ['group', 'supergroup']:

        logger.debug('KO3')
        logger.debug(message)
        logger.debug(message.from_user)
        logger.debug('KOK4')

        await bot.reply_to(message, message.text)
