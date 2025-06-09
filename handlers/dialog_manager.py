from services.dialog import dialog
from utils.util import send_text

class DialogManager:
    def __init__(self, dialog):
        self.dialog = dialog

    async def dialog_mode(self, update, context):
        user_id = update.effective_user.id
        mode = self.dialog.get_mode(user_id)
        print(f"[DEBUG] dialog_mode for user {user_id} with mode {mode}")
        print(f"[DialogMode] User {user_id} mode = {mode}")

        if mode == 'random_fact':
            await self.random_fact(update, context)
        elif mode == 'gpt':
            await send_text(update, context, f"GPT-mode {update.effective_user.first_name}")
            await self.gpt_dialog(update, context)
        elif mode and mode.startswith('talk'):
            await self.talk_dialog(update, context)
        elif mode == 'quiz':
            from handlers.quiz import handle_quiz_answer
            await handle_quiz_answer(update, context)
        elif mode == 'photo':
            await self.photo_handler(update, context)
        elif mode == 'recept':
            await self.recept_dialog(update, context)
        else:
            await send_text(update, context, "📭 Невідомий режим. Введіть /start, щоб повернутись у меню.")
    async def random_fact(self, update, context):
        from handlers.facts import random_fact as rf
        await rf(update, context)

    async def gpt_dialog(self, update, context):
        from handlers.gpt_chat import gpt_dialog as gd
        await gd(update, context)

    async def talk_dialog(self, update, context):
        from handlers.talk import talk_dialog as td
        await td(update, context)

    # async def photo_handler(self, update, context):
    #     from handlers.photo import photo_handler as ph
    #     await ph(update, context)
    #
    # async def recept_dialog(self, update, context):
    #     from handlers.recept import recept_dialog as rd
    #     await rd(update, context)


# Ініціалізація менеджера діалогів
dialog_manager = DialogManager(dialog)


# Функція, яку треба реєструвати в Telegram як обробник текстових повідомлень
async def dialog_mode(update, context):
    await dialog_manager.dialog_mode(update, context)
