from telegram import ReplyKeyboardMarkup
from services.dialog import dialog
from utils.util import load_message, send_photo, send_text, show_main_menu, send_text_buttons
from utils.logger import logger, log_user_action
from handlers.facts import random_fact
from handlers.gpt_chat import gpt
from handlers.talk import talk_command
from handlers.quiz import handle_quiz_command
from handlers.food_analysis import photo_mode_start
from handlers.recipe import recept

async def start(update, context):
    user_id = update.effective_user.id
    dialog.set_mode(user_id, 'main')  # Встановлюємо режим main при старті

    # keyboard = [["🎲 Цікавий факт", "💬 GPT-чат"],
    #             ["🧠 Особистість", "🎓 Вікторина"],
    #             ["🍳 Рецепт", "📷 Фото"]]
    # reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    msg = load_message('main')
    await send_photo(update, context, 'avatar_main')
    # await send_text(update, context, msg)
    await show_main_menu(update, context, {
    'start': '🏠 Головне меню бота',
    'random': '🎲 Цікавий факт',
    'gpt': '💬 Спілкування з ChatGPT',
    'talk': '🧠 Діалог з історичною особистістю',
    'quiz': '🎓 Інтелектуальна гра "Найрозумніший"',
    'photo': '📷 Розпізнавання їжі та підрахунок калорій',
    'recept': '🍳 Кулінарний помічник (рецепти зі своїх інгредієнтів)',
    })
    await send_text_buttons(update, context, msg, {
        'main_start': '🏠 Головне меню бота',
        'main_random': '🎲 Цікавий факт',
        'main_gpt': '💬 Спілкування з ChatGPT',
        'main_talk': '🧠 Діалог з історичною особистістю',
        'main_quiz': '🎓 Інтелектуальна гра "Найрозумніший"',
        'main_photo': '📷 Розпізнавання їжі та підрахунок калорій',
        'main_recept': '🍳 Кулінарний помічник',
    })

async def main_button(update, context):
    callback = update.callback_query
    query_data = callback.data
    user = callback.from_user
    user_id = user.id

    dialog.set_mode(user_id, 'main')

    await callback.answer()  # завжди відповідаємо на callback_query
    log_user_action(update, f"натиснув кнопку: {query_data}")

    if query_data == 'main_start':
        await start(update, context)
    elif query_data == 'main_random':
        await random_fact(update, context)
    elif query_data == 'main_gpt':
        await gpt(update, context)
    elif query_data == 'main_talk':
        await talk_command(update, context)
    elif query_data == 'main_quiz':
        await handle_quiz_command(update, context)
    elif query_data == 'main_photo':
        await photo_mode_start(update, context)
    elif query_data == 'main_recept':
        await recept(update,context)
    else:
        await callback.message.edit_text("⚠️ Невідома команда.")

