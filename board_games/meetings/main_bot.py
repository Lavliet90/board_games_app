from telebot.async_telebot import AsyncTeleBot

from board_games.board_games import settings

bot = AsyncTeleBot(settings.TOKEN_BOT, parse_mode='HTML')


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    print('KOK')
    text = 'Hi, I am EchoBot.\nJust write me something and I will repeat it!'
    await bot.reply_to(message, text)


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    print('KOK')
    await bot.reply_to(message, message.text)
