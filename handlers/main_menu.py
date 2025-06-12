from telegram import ReplyKeyboardMarkup
from services.dialog import dialog
from utils.util import load_message, send_photo, send_text, show_main_menu

async def start(update, context):
    user_id = update.effective_user.id
    dialog.set_mode(user_id, 'main')  # Встановлюємо режим main при старті

    keyboard = [["🎲 Цікавий факт", "💬 GPT-чат"],
                ["🧠 Особистість", "🎓 Вікторина"],
                ["🍳 Рецепт", "📷 Фото"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    msg = load_message('main')
    await send_photo(update, context, 'avatar_main')
    await send_text(update, context, msg)
    await show_main_menu(update, context, {
        'start': 'головне меню бота',
        'random': 'цікавий факт',
        'gpt': 'розмова зі ШІ',
        'talk': 'Діалог з відомою особистістю',
        'quiz': 'гра "Самий розумний"',
        'photo': 'Компьютерний зір',
        'recept': 'Кулінарний помічник',
    })

    # Уніфіковано обробляємо ситуацію message або callback
    # message = update.message or (update.callback_query and update.callback_query.message)
    # if message:
    #     await message.reply_text("👋 Привіт! Обери опцію:", reply_markup=reply_markup)
    # else:
    #     await context.bot.send_message(chat_id=update.effective_user.id,
    #                                    text="👋 Привіт! Обери опцію:",
    #                                    reply_markup=reply_markup)
