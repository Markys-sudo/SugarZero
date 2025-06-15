import os
import uuid
from telegram import Update
from telegram.ext import ContextTypes
from utils.util import send_text, send_text_buttons, load_prompt
from services.dialog import dialog
from services.gpt import chatgpt
from services.nutrition_service import NutritionService
from utils.logger import logger, log_user_action
from handlers.food_diary import add_diary_entry

nutrition = NutritionService()

async def photo_mode_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dialog.set_mode(user_id, 'photo_mode')
    await send_text(update, context, "📸 Надішліть фото страви, я проаналізую її та порахую калорії.")


nutrition = NutritionService()

async def photo_mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_user_action(update, "📸 Надіслав(-ла) фото для аналізу")

    # Завантаження фото
    photo = update.message.photo[-1]
    file_id = str(uuid.uuid4())
    file_path = f"temp/{file_id}.jpg"
    os.makedirs("temp", exist_ok=True)

    try:
        photo_file = await context.bot.get_file(photo.file_id)
        await photo_file.download_to_drive(file_path)
        logger.info(f"[{user_id}] Фото збережено у {file_path}")
        await send_text(update, context, "🧠 Аналізую фото...")
    except Exception as e:
        logger.exception(f"[{user_id}] ❌ Помилка при завантаженні фото: {e}")
        await send_text(update, context, "❌ Не вдалося завантажити фото. Спробуйте ще раз.")
        return

    # GPT-опис
    description = await chatgpt.describe_image(file_path)
    logger.info(f"[{user_id}] Опис зображення: {description}")
    await send_text(update, context, f"📝 Опис зображення:\n\n{description}")

    # GPT-інгредієнти
    prompt = load_prompt('food')
    ingredients_raw = await chatgpt.send_question(prompt, description)
    logger.info(f"[{user_id}] Список інгредієнтів (GPT):\n{ingredients_raw}")
    await send_text(update, context, f"🥦 Інгредієнти:\n{ingredients_raw}")

    # Корекція назв
    mapping = {
        "mashed potatoes": "boiled potatoes",
        "black pepper": "ground black pepper",
        "fried egg": "egg, fried",
        "scrambled eggs": "egg, scrambled",
        "boiled egg": "egg, boiled"
    }

    ingredients_list = [
        i.strip().strip("',\"").lower()
        for i in ingredients_raw.split("\n")
        if i.strip()
    ]
    corrected = [mapping.get(x, x) for x in ingredients_list]
    logger.info(f"[{user_id}] Виправлені інгредієнти: {corrected}")

    # Зберігаємо
    dialog.set_data(user_id, "last_ingredients", "\n".join(corrected))

    # Калорійність
    nutrition_info = await nutrition.get_nutrition("\n".join(corrected), user_id=user_id)
    logger.info(f"[{user_id}] Калорійність:\n{nutrition_info}")

    await send_text_buttons(update, context, f"🔥 Калорійність:\n{nutrition_info}", {
        "edit_ingredients": "✏️ Редагувати інгредієнти",
        "add_to_diary": "➕ Додати в щоденник",
        "main_start": "🏠 Головне меню"
    })

    try:
        os.remove(file_path)
        logger.info(f"[{user_id}] Тимчасовий файл {file_path} видалено")
    except Exception as e:
        logger.warning(f"[{user_id}] Не вдалося видалити файл {file_path}: {e}")

async def handle_edit_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    dialog.set_mode(user_id, "edit_ingredients")
    log_user_action(update, "✏️ Редагування інгредієнтів")
    await send_text(update, context, "✏️ Введіть інгредієнти англійською по рядку.")

async def handle_edit_ingredients_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if dialog.get_mode(user_id) != "edit_ingredients":
        return

    text = update.message.text.strip()
    if not text:
        await send_text(update, context, "❌ Будь ласка, введіть список інгредієнтів.")
        return

    dialog.set_data(user_id, "last_ingredients", text)
    await send_text(update, context, "🔄 Перераховую калорії...")

    nutrition_info = await nutrition.get_nutrition(text, user_id=user_id)
    dialog.set_mode(user_id, "photo_mode")

    await send_text_buttons(update, context, f"🔥 Калорійність:\n{nutrition_info}", {
        "edit_ingredients": "✏️ Редагувати ще раз",
        "add_to_diary": "➕ Додати в щоденник",
        "main_start": "🏠 Головне меню"
    })

async def handle_add_to_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    txt = dialog.get_data(user_id, "last_ingredients")
    if not txt:
        await query.edit_message_text("❌ Немає даних для щоденника.")
        return

    add_diary_entry(user_id, txt)
    await query.edit_message_text("✅ Додано до щоденника.")
