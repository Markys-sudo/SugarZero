from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.main_menu import start
from handlers.dialog_manager import dialog_mode
from handlers.facts import random_fact, button_fact
from handlers.gpt_chat import gpt,gpt_dialog
from handlers.talk import talk_button, talk_command, talk_dialog
from handlers.quiz import handle_quiz_command, handle_quiz_button, handle_quiz_answer

def register_all_handlers(app):
    # Основне меню
    app.add_handler(CommandHandler("start", start))

    # Цікаві факти
    app.add_handler(CommandHandler('random', random_fact))
    app.add_handler(CallbackQueryHandler(button_fact, pattern="^fact_.*"))

    #GPT чат
    app.add_handler(CommandHandler('gpt', gpt))


    #Talk
    app.add_handler(CommandHandler('talk', talk_command))
    app.add_handler(CallbackQueryHandler(talk_button))


    #quiz
    # Команда /quiz
    app.add_handler(CommandHandler('quiz', handle_quiz_command))
    app.add_handler(CallbackQueryHandler(handle_quiz_answer, pattern=r'^quiz_[ABCD]$'))
    app.add_handler(CallbackQueryHandler(handle_quiz_button, pattern=r'^quiz_(science|world|culture|history|end)$'))


    #dialog mode
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), dialog_mode))
