# handlers/food_diary.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils.util import send_text_buttons_edit, send_text
from services.dialog import dialog
from database.food_diary_db import add_diary_entry, get_diary_entries, clear_diary


async def food_diary_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dialog.set_mode(user_id, "food_diary")
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

    if data == "add_food_entry":
        dialog.set_mode(user_id, "adding_food_entry")
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
        await send_text_buttons_edit(update, context,
            "🗑 Щоденник очищено.",
            {"food_diary": "🔙 Назад до щоденника"}
        )

    elif data == "food_diary":
        await food_diary_start(update, context)

    elif data == "main_start":
        from handlers.main_menu import start  # або ваш старт-хендлер
        dialog.set_mode(user_id, "main")
        await start(update, context)

async def handle_food_entry_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = dialog.get_mode(user_id)
    if mode != "adding_food_entry":
        return  # не в режимі додавання — ігноруємо

    text = update.message.text.strip()
    if text:
        add_diary_entry(user_id, text)
        await send_text(update, context, "✅ Додано до щоденника.")
    else:
        await send_text(update, context, "⚠️ Порожнє — спробуйте ще раз.")

    # Повернутися до меню щоденника
    await food_diary_start(update, context)
