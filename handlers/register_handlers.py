from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters

from handlers.main_menu import start, main_button
from handlers.facts import random_fact, button_fact
from handlers.gpt_chat import gpt, gpt_dialog
from handlers.talk import talk_button, talk_command, talk_dialog
from handlers.quiz import handle_quiz_command, handle_quiz_button, handle_quiz_answer
from handlers.recipe import recept, button_recept  # recept = /recept, button_recept = обробка кнопок
from handlers.dialog_manager import dialog_mode
from handlers.food_analysis import photo_mode_start, photo_mode_handler
from utils.util import send_text
from services.dialog import dialog


# Фото: визначення режиму
async def unified_photo_handler(update, context):
    user_id = update.effective_user.id
    mode = dialog.get_mode(user_id)

    if mode == 'photo_mode':
        await photo_mode_handler(update, context)
    else:
        await send_text(update, context, "📷 Надішліть /photo перед надсиланням зображення страви.")


def register_all_handlers(app):

    # Основне меню
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(main_button, pattern="^main_.*"))
    # Цікаві факти
    app.add_handler(CommandHandler('random', random_fact))
    app.add_handler(CallbackQueryHandler(button_fact, pattern="^fact_.*"))

    # GPT чат
    app.add_handler(CommandHandler('gpt', gpt))

    # Talk з відомими особистостями
    app.add_handler(CommandHandler('talk', talk_command))
    app.add_handler(CallbackQueryHandler(talk_button, pattern=r'^talk_'))

    # Вікторина
    app.add_handler(CommandHandler('quiz', handle_quiz_command))
    app.add_handler(CallbackQueryHandler(handle_quiz_answer, pattern=r'^quiz_[ABCD]$'))
    app.add_handler(CallbackQueryHandler(handle_quiz_button, pattern=r'^quiz_(science|world|culture|history|end)$'))

    # Фото-режим
    app.add_handler(CommandHandler('photo', photo_mode_start))
    app.add_handler(MessageHandler(filters.PHOTO, unified_photo_handler))

    # Рецепти
    app.add_handler(CommandHandler('recept', recept))  # старт рецепта
    app.add_handler(CallbackQueryHandler(button_recept, pattern=r'^recept_'))  # кнопки рецепта

    # Обробка ТЕКСТУ — залежно від активного dialog.mode
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), dialog_mode))
