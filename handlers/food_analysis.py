# handlers/food_analysis.py
from services.dialog import dialog
import os
import uuid
from telegram import Update
from telegram.ext import ContextTypes
from utils.util import send_text
from services.gpt import chatgpt
from services.nutrition_service import NutritionService

async def photo_mode_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dialog.set_mode(user_id, 'photo_mode')
    await send_text(update, context, "📸 Надішліть фото страви, я проаналізую її та порахую калорії.")


nutrition = NutritionService()

async def photo_mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo = update.message.photo[-1]
    file_id = str(uuid.uuid4())
    file_path = f"temp/{file_id}.jpg"
    os.makedirs("temp", exist_ok=True)

    try:
        # Завантаження фото
        photo_file = await context.bot.get_file(photo.file_id)
        await photo_file.download_to_drive(file_path)
        await send_text(update, context, "🧠 Аналізую фото через GPT...")
    except Exception as e:
        await send_text(update, context, "❌ Не вдалося завантажити фото. Спробуйте ще раз.")
        return

    # GPT опис
    description = await chatgpt.describe_image(file_path)
    await send_text(update, context, f"📝 Опис зображення:\n\n{description}")

    # GPT: інгредієнти
    prompt = (
        "На основі цього опису страви сформуй список інгредієнтів англійською мовою, "
        "один інгредієнт на рядок. Додай приблизну кількість. Формат повинен бути як: "
        "'2 potatoes', '1 tsp ground black pepper', '1 tbsp olive oil'. "
        "Без пояснень, тільки список."
    )
    ingredients_raw = await chatgpt.send_question(prompt, description)
    print(ingredients_raw, type(ingredients_raw), 'ingredients_raw')
    await send_text(update, context, f"🥦 Інгредієнти:\n{ingredients_raw}")

    # 🔧 Виправлення назв інгредієнтів для Spoonacular
    ingredient_mapping = {
        "mashed potatoes": "boiled potatoes",
        "black pepper": "ground black pepper",
        "fried egg": "egg, fried",
        "scrambled eggs": "egg, scrambled",
        "boiled egg": "egg, boiled"
        # додай інші при потребі
    }

    ingredients_list = [i.strip().lower() for i in ingredients_raw.split(",")]
    corrected_ingredients = [
        ingredient_mapping.get(item, item) for item in ingredients_list
    ]
    ingredients_fixed = ", ".join(corrected_ingredients)

    # Калорії та БЖУ
    nutrition_info = await nutrition.get_nutrition(ingredients_fixed)
    print('nutrition_info', nutrition_info, type(nutrition_info))
    await send_text(update, context, f"🔥 Калорійність:\n{nutrition_info}")

    # Прибирання тимчасового файлу
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Не вдалося видалити файл {file_path}: {e}")