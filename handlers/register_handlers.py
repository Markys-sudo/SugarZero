from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.main_menu import start, main_button
from handlers.facts import random_fact, button_fact
from handlers.gpt_chat import gpt, gpt_dialog
from handlers.talk import talk_button, talk_command, talk_dialog
from handlers.quiz import handle_quiz_command, handle_quiz_button, handle_quiz_answer
from handlers.recipe import recept, button_recept
from handlers.dialog_manager import dialog_mode
from handlers.food_diary import food_diary_start, handle_diary_buttons
from handlers.food_analysis import (
    photo_mode_start,
    photo_mode_handler,
    handle_edit_ingredients,
    handle_edit_ingredients_input,
    handle_add_to_diary
)
from telegram.ext import ContextTypes
from services.dialog import dialog
from utils.util import send_text

async def unified_photo_handler(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = dialog.get_mode(user_id)

    # Якщо користувач у режимі 'photo_mode' — аналізуємо
    if mode == 'photo_mode':
        await photo_mode_handler(update, context)
    else:
        # Якщо не в режимі — підказуємо, як увімкнути режим
        await send_text(update, context,
            "📷 Ви надіслали фото, але спочатку потрібно активувати режим аналізу.\n"
            "Надішліть команду /photo, щоб розпочати."
        )

def register_all_handlers(app):

    # Основне меню
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(main_button, pattern="^main_.*"))

    # Цікаві факти
    app.add_handler(CommandHandler('random', random_fact))
    app.add_handler(CallbackQueryHandler(button_fact, pattern="^fact_.*"))

    # GPT-чат
    app.add_handler(CommandHandler('gpt', gpt))

    # Talk
    app.add_handler(CommandHandler('talk', talk_command))
    app.add_handler(CallbackQueryHandler(talk_button, pattern=r'^talk_'))

    # Вікторина
    app.add_handler(CommandHandler('quiz', handle_quiz_command))
    app.add_handler(CallbackQueryHandler(handle_quiz_answer, pattern=r'^quiz_[ABCD]$'))
    app.add_handler(CallbackQueryHandler(handle_quiz_button, pattern=r'^quiz_(science|world|culture|history|end)$'))

    # Фото-режим
    app.add_handler(CommandHandler('photo', photo_mode_start))
    app.add_handler(MessageHandler(filters.PHOTO, unified_photo_handler))
    app.add_handler(CallbackQueryHandler(handle_edit_ingredients, pattern="^edit_ingredients$"))
    app.add_handler(CallbackQueryHandler(handle_add_to_diary, pattern="^add_to_diary$"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_edit_ingredients_input))

    # Рецепти
    app.add_handler(CommandHandler('recept', recept))
    app.add_handler(CallbackQueryHandler(button_recept, pattern=r'^recept_'))

    # Щоденник харчування
    app.add_handler(CommandHandler("diary", food_diary_start))
    app.add_handler(CallbackQueryHandler(handle_diary_buttons, pattern="^(add_food_entry|view_food_diary|clear_food_diary|food_diary|main_start)$"))

    # Обробка тексту залежно від режима
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), dialog_mode))
