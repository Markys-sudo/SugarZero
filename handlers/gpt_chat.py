from services.gpt import chatgpt
from utils.util import send_photo, load_message, send_text
from utils.logger import gpt_logger
from services.dialog import dialog

class GPTService:
    def __init__(self, dialog):
        self.dialog = dialog
        self.mode_name = 'gpt'

    async def gpt(self, update, context):  # додано self
        user_id = update.effective_user.id
        self.dialog.set_mode(user_id, 'gpt')  # звертаємось до self.dialog

        await send_text(update, context, "Режим GPT активовано. Напишіть ваше повідомлення.")

    async def start_gpt(self, update, context):
        user_id = update.effective_user.id
        self.dialog.set_mode(user_id, self.mode_name)
        await send_photo(update, context, 'gpt')
        msg = load_message('gpt')
        await send_text(update, context, msg)

    async def handle_message(self, update, context):
        text = update.message.text if update.message and update.message.text else ''
        if not text:
            return  # Пропускаємо порожнє повідомлення

        user_id = update.effective_user.id
        gpt_logger.info(f"[{user_id}] GPT: {text}")

        try:
            answer = await chatgpt.add_message(text)
            await send_text(update, context, answer)
        except Exception as e:
            await send_text(update, context, f"⚠️ Виникла помилка при зверненні до GPT: {e}")


# Ініціалізація екземпляра
gpt_service = GPTService(dialog)

# Обгортки для хендлерів
async def gpt(update, context):
    await gpt_service.start_gpt(update, context)

async def gpt_dialog(update, context):
    user_id = update.effective_user.id
    current_mode = dialog.get_mode(user_id)  # отримуємо поточний режим
    if current_mode != 'gpt':
        return  # якщо режим не GPT — нічого не робимо
    await gpt_service.handle_message(update, context)