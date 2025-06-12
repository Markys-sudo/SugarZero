from services.dialog import dialog
from services.gpt import chatgpt
from utils.util import load_prompt, load_message, send_text_buttons, send_text, send_photo
from utils.logger import log_user_action, gpt_logger
from handlers.main_menu import start
from database.db import save_user, add_favorite, get_favorites  # твої функції

class ReceptHandler:
    def __init__(self, dialog):
        self.dialog = dialog
        self.mode = 'recept'

    async def handle_command(self, update, context):
        user = update.effective_user
        save_user(user)
        self.dialog.set_mode(user.id, self.mode)

        await send_photo(update, context, 'recept')
        msg = load_message('recept')
        await send_text(update, context, msg)

    async def handle_dialog(self, update, context):
        if self.dialog.get_mode(update.effective_user.id) != self.mode:
            return

        text = update.message.text if update.message and update.message.text else ''
        if not text:
            return

        context.user_data['ingredients'] = text
        chatgpt.message_list.clear()

        gpt_logger.info(f"[{update.effective_user.id}] GPT: {text}")
        try:
            prompt_template = load_prompt('recept')
            prompt = prompt_template.format(ingredients=text)
            chatgpt.set_prompt(prompt)
            answer = await chatgpt.send_message_list()

            await send_text_buttons(update, context, answer, {
                "recept_next": 'Ще рецепти',
                "recept_save": '📌 Додати в обране',
                "recept_favorites": '🍴 Мої обрані рецепти',
                "recept_end": 'Закінчити'
            })
        except Exception as e:
            await send_text(update, context, f"⚠️ Виникла помилка при зверненні до GPT: {e}")

    async def handle_button(self, update, context):
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        log_user_action(update, f"натиснув: {query.data}")

        if query.data == 'recept_next':
            ingredients = context.user_data.get('ingredients', '')
            prompt = load_prompt('recept').format(ingredients=ingredients)
            chatgpt.set_prompt(prompt)
            answer = await chatgpt.send_message_list()
            await send_text_buttons(update, context, answer, {
                "recept_next": 'Ще рецепти',
                "recept_save": '📌 Додати в обране',
                "recept_favorites": '🍴 Мої обрані рецепти',
                "recept_end": 'Закінчити'
            })

        elif query.data == 'recept_save':
            recipe_text = query.message.text
            add_favorite(user_id, recipe_text)
            await send_text(update, context, "✅ Рецепт додано до обраного!")

        elif query.data == 'recept_favorites':
            favs = get_favorites(user_id)
            if not favs:
                await send_text(update, context, "📭 У вас ще немає збережених рецептів.")
            else:
                await send_text(update, context, "📚 Ваші улюблені рецепти:")
                for recipe in favs:
                    await send_text(update, context, recipe)

        elif query.data == 'recept_end':
            self.dialog.set_mode(user_id, 'main')
            await start(update, context)

# Ініціалізація
recept_handler = ReceptHandler(dialog)

# Хендлери для підключення до диспетчера
async def recept(update, context):
    await recept_handler.handle_command(update, context)

async def recept_dialog(update, context):
    await recept_handler.handle_dialog(update, context)

async def button_recept(update, context):
    await recept_handler.handle_button(update, context)
