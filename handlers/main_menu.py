from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from utils.util import *


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🎲 Цікавий факт", "💬 GPT-чат"],
                ["🧠 Особистість", "🎓 Вікторина"],
                ["🍳 Рецепт", "📷 Фото"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("👋 Привіт! Обери опцію:", reply_markup=reply_markup)

async def start(update, context):
    #dialog.mode = 'main'
    msg = load_message('main')
    await send_photo(update, context,'avatar_main')
    await send_text(update, context, msg)
    await show_main_menu(update, context,{
        'start':'головне меню бота',
        'random': 'цікавий факт',
        'gpt' : 'розмова зі ШІ',
        'talk' : 'Діалог з відомою особистістю',
        'quiz' : 'гра "Самий розумний"',
        'photo' : 'Компьютерний зір',
        'recept': 'Кулінарний помічник',

    })
    #chatgpt.message_list.clear()