from services.dialog import dialog
from utils.util import send_text
from handlers.recipe import recept_handler  # вже містить recept_dialog, button_recept тощо
from handlers.food_analysis import photo_mode_handler, handle_edit_ingredients_input
from handlers.food_diary import handle_food_entry_input

class DialogManager:
    def __init__(self, dialog):
        self.dialog = dialog
        self.photo_food_handler = photo_mode_handler
        self.recept_handler = recept_handler

    async def dialog_mode(self, update, context):
        user_id = update.effective_user.id
        mode = self.dialog.get_mode(user_id)
        print(f"[DEBUG] dialog_mode for user {user_id} with mode {mode}")
        print(f"[DialogMode] User {user_id} mode = {mode}")

        if mode == 'random_fact':
            await self.random_fact(update, context)
        elif mode == 'gpt':
            await self.gpt_dialog(update, context)
        elif mode and mode.startswith('talk'):
            await self.talk_dialog(update, context)
        elif mode == 'quiz':
            await self.quiz_dialog(update, context)
        elif mode == 'photo_mode':
            await self.photo_food_handler.handle_photo(update, context)
        elif mode == 'food_correction':
            await self.photo_food_handler.handle_corrections(update, context)
        elif mode == 'recept':
            await self.recept_handler.handle_dialog(update, context)
        elif mode == 'edit_ingredients':
            await handle_edit_ingredients_input(update, context)
        elif mode == "adding_food_entry":
            await handle_food_entry_input(update, context)


        else:
            await send_text(update, context, "📭 Невідомий режим. Введіть /start, щоб повернутись у меню.")

    async def random_fact(self, update, context):
        from handlers.facts import random_fact
        await random_fact(update, context)

    async def gpt_dialog(self, update, context):
        from handlers.gpt_chat import gpt_dialog
        await gpt_dialog(update, context)

    async def talk_dialog(self, update, context):
        from handlers.talk import talk_dialog
        await talk_dialog(update, context)

    async def quiz_dialog(self, update, context):
        from handlers.quiz import handle_quiz_answer
        await handle_quiz_answer(update, context)

# Ініціалізація менеджера діалогів
dialog_manager = DialogManager(dialog)

# Обробник текстових повідомлень
async def dialog_mode(update, context):
    await dialog_manager.dialog_mode(update, context)
