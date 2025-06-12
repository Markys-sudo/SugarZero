from telegram import ReplyKeyboardMarkup
from services.dialog import dialog
from utils.util import load_message, send_photo, send_text, show_main_menu

async def start(update, context):
    user_id = update.effective_user.id
    dialog.set_mode(user_id, 'main')  # Встановлюємо режим main при старті

    # keyboard = [["🎲 Цікавий факт", "💬 GPT-чат"],
    #             ["🧠 Особистість", "🎓 Вікторина"],
    #             ["🍳 Рецепт", "📷 Фото"]]
    # reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    msg = load_message('main')
    await send_photo(update, context, 'avatar_main')
    await send_text(update, context, msg)
    await show_main_menu(update, context, {
    'start': '🏠 Головне меню бота',
    'random': '🎲 Цікавий факт',
    'gpt': '💬 Спілкування з ChatGPT',
    'talk': '🧠 Діалог з історичною особистістю',
    'quiz': '🎓 Інтелектуальна гра "Найрозумніший"',
    'photo': '📷 Розпізнавання їжі та підрахунок калорій',
    'recept': '🍳 Кулінарний помічник (рецепти зі своїх інгредієнтів)',
    })

    # Уніфіковано обробляємо ситуацію message або callback
    # message = update.message or (update.callback_query and update.callback_query.message)
    # if message:
    #     await message.reply_text("👋 Привіт! Обери опцію:", reply_markup=reply_markup)
    # else:
    #     await context.bot.send_message(chat_id=update.effective_user.id,
    #                                    text="👋 Привіт! Обери опцію:",
    #                                    reply_markup=reply_markup)
