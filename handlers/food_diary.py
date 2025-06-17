# handlers/food_diary.py
from services.nutrition_service import NutritionService
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils.util import send_text_buttons_edit, send_text
from services.dialog import dialog
from database.food_diary_db import add_diary_entry, get_diary_entries, clear_diary
from utils.logger import log_user_action, dialog_logger


async def food_diary_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    dialog.set_mode(user_id, "food_diary")
    dialog_logger.info(f"[{user_id}] Режим встановлено: food_diary")
    log_user_action(update, "Відкрив Щоденник харчування")
    await send_text_buttons_edit(update, context, "📘 Щоденник харчування — оберіть дію:", {
        "add_food_entry": "➕ Додати страву",
        "view_food_diary": "📋 Переглянути сьогодні",
        #"calc_food_diary": "🧮 Порахувати калорії",
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
    log_user_action(update, f"Поточний режим: {mode}")

    # if data == "add_food_entry":
    #     dialog.set_mode(user_id, "adding_food_entry")
    #     dialog_logger.info(f"[{user_id}] Режим встановлено: adding_food_entry")
    #     await send_text_buttons_edit(update, context,
    #         "📝 Введіть страву (наприклад: `2 eggs`):",
    #         {"food_diary": "🔙 Назад до щоденника"}
    #     )
    # elif data == "view_food_diary":
    #     entries = get_diary_entries(user_id)
    #     text = "📋 Сьогодні:\n\n" + "\n".join(f" {e}" for e in entries) if entries else "📭 Щоденник порожній."
    #     await send_text_buttons_edit(update, context, text, {
    #         "food_diary": "🔙 Назад до щоденника"
    #     })
    if data == "add_food_entry":
        dialog.set_mode(user_id, "adding_food_entry")
        dialog_logger.info(f"[{user_id}] Режим встановлено: adding_food_entry")

        text = (
            "📝 Введіть страву у форматі англійською з приблизною кількістю:\n\n"
            "Наприклад:\n"
            "2 boiled eggs\n"
            "100g fried chicken\n"
            "1 tbsp olive oil\n\n"
            "Можна ввести одну або кілька позицій (кожна з нового рядка)."
        )

        await send_text_buttons_edit(update, context, text, {
            "food_diary": "🔙 Назад до щоденника"
        })

    elif data == "view_food_diary":
        entries = get_diary_entries(user_id)

        if not entries:
            await send_text_buttons_edit(update, context, "📭 Щоденник порожній.", {
                "food_diary": "🔙 Назад до щоденника"
            })
            return

        ingredients_text = "\n".join(entries)

        try:

            nutrition_service = NutritionService()
            summary = await nutrition_service.get_nutrition_summary(ingredients_text, user_id)
            # summary = (
            #         f"📋 Сьогодні:\n\n" + "\n".join(f"{e}" for e in entries) +
            #         f"\n\n🍽 Усього:\n"
            #         f"Калорії: {nutrition['calories']} ккал\n"
            #         f"Білки: {nutrition['protein']} г\n"
            #         f"Жири: {nutrition['fat']} г\n"
            #         f"Вуглеводи: {nutrition['carbs']} г"
            # )
        except Exception as e:

            dialog_logger.exception(f"[{user_id}] Помилка при отриманні нутрієнтів: {e}")
            summary = (
                    f"📋 Сьогодні:\n\n" + "\n".join(f"{e}" for e in entries) +
                    f"\n\n⚠️ Не вдалося обчислити калорії."
            )

        await send_text_buttons_edit(update, context, summary, {
            "food_diary": "🔙 Назад до щоденника"
        })
    elif data == "calc_food_diary":
        entries = get_diary_entries(user_id)
        if not entries:
            await send_text_buttons_edit(update, context, "📭 Щоденник порожній.", {
                "food_diary": "🔙 Назад до щоденника"
            })
            return

        try:
            ingredients_text = "\n".join(entries)
            nutrition_service = NutritionService()
            nutrition = await nutrition_service.get_nutrition_summary(ingredients_text,user_id)
            # nutrition = await nutrition_service.get_nutrition(ingredients_text)
            #
            # text = (
            #     f"🍽 Підсумок по щоденнику:\n"
            #     f"Калорії: {nutrition['calories']} ккал\n"
            #     f"Білки: {nutrition['protein']} г\n"
            #     f"Жири: {nutrition['fat']} г\n"
            #     f"Вуглеводи: {nutrition['carbs']} г"
            # )
        except Exception as e:

            dialog_logger.exception(f"[{user_id}] Помилка при обчисленні калорій: {e}")
            text = "⚠️ Не вдалося обчислити калорії."

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
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            add_diary_entry(user_id, line)
            log_user_action(update, f"Додав до щоденника: {line}")

        await send_text(update, context, "✅ Додано до щоденника.")

    else:
        log_user_action(update, "Надіслано порожнє повідомлення під час додавання до щоденника")
        await send_text(update, context, "⚠️ Порожнє — спробуйте ще раз.")

    await food_diary_start(update, context)
