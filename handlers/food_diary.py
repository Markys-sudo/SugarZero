# handlers/food_diary.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils.util import send_text_buttons_edit, send_text
from services.dialog import dialog
from database.food_diary_db import add_diary_entry, get_diary_entries, clear_diary
from utils.logger import log_user_action, dialog_logger


async def food_diary_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dialog.set_mode(user_id, "food_diary")
    log_user_action(update, "Відкрив Щоденник харчування")
    await send_text_buttons_edit(update, context, "📘 Щоденник харчування — оберіть дію:", {
        "add_food_entry": "➕ Додати страву",
        "view_food_diary": "📋 Переглянути сьогодні",
        "clear_food_diary": "🗑 Очистити",
        "main_start": "🏠 Головне меню"
    })


async def handle_diary_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    log_user_action(update, f"Натиснув кнопку: {data}")
    mode = dialog.get_mode(user_id)
    dialog_logger.debug(f"[{user_id}] Поточний режим: {mode}")


    if data == "add_food_entry":
        dialog.set_mode(user_id, "adding_food_entry")
        dialog_logger.info(f"[{user_id}] Режим встановлено: adding_food_entry")
        await send_text_buttons_edit(update, context,
            "📝 Введіть страву (наприклад: `2 eggs`):",
            {"food_diary": "🔙 Назад до щоденника"}
        )
    elif data == "view_food_diary":
        entries = get_diary_entries(user_id)
        text = "📋 Сьогодні:\n\n" + "\n".join(f" {e}" for e in entries) if entries else "📭 Щоденник порожній."
        await send_text_buttons_edit(update, context, text, {
            "food_diary": "🔙 Назад до щоденника"
        })

    elif data == "clear_food_diary":
        clear_diary(user_id)
        log_user_action(update, "Очистив щоденник харчування")
        await send_text_buttons_edit(update, context,
            "🗑 Щоденник очищено.",
            {"food_diary": "🔙 Назад до щоденника"}
        )

    elif data == "food_diary":
        await food_diary_start(update, context)

    elif data == "main_start":
        from handlers.main_menu import start
        dialog.set_mode(user_id, "main")
        log_user_action(update, "Повернувся до головного меню")
        await start(update, context)

from utils.logger import dialog_logger
async def handle_food_entry_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = dialog.get_mode(user_id)
    text = update.message.text.strip()
    dialog_logger.info(f"[{user_id}] У режимі '{mode}' ввів: {text}")

    if mode != "adding_food_entry":
        dialog_logger.debug(f"[{user_id}] Отримано повідомлення поза режимом додавання — ігнорується")
        return

    text = update.message.text.strip()
    if text:
        add_diary_entry(user_id, text)
        log_user_action(update, f"Додав до щоденника: {text}")
        await send_text(update, context, "✅ Додано до щоденника.")
    else:
        log_user_action(update, "Надіслано порожнє повідомлення під час додавання до щоденника")
        await send_text(update, context, "⚠️ Порожнє — спробуйте ще раз.")

    await food_diary_start(update, context)
