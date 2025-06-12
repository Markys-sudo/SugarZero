from services.dialog import dialog
from services.gpt import chatgpt
from utils.util import load_prompt, send_text_buttons, send_text, send_photo
from utils.logger import log_user_action, dialog_logger
from handlers.main_menu import start

class FactGenerator:
    def __init__(self, dialog):
        self.dialog = dialog
        self.prompt_key = "random_fact"

    async def handle_command(self, update, context):
        user_id = update.effective_user.id
        text = update.message.text if update.message and update.message.text else ''
        log_user_action(update, f"написав: {text}")
        dialog_logger.info(f"[{user_id}] Обробка команди /random")

        self.dialog.set_mode(user_id, 'random_fact')
        dialog_logger.info(f"[{user_id}] Режим встановлено: random_fact")

        await send_photo(update, context, 'fact')

        try:
            answer = await self.generate_fact(text)
            await self.send_response(update, context, answer)
        except Exception as e:
            await self.handle_error(update, context, e)

    async def handle_button(self, update, context):
        query = update.callback_query
        await query.answer()
        user_id = update.effective_user.id
        log_user_action(update, f"натиснув кнопку: {query.data}")
        dialog_logger.info(f"[{user_id}] Натиснута кнопка: {query.data}")

        if query.data == 'fact_random':
            try:
                self.dialog.set_mode(user_id, 'random_fact')
                dialog_logger.info(f"[{user_id}] Режим залишено: random_fact")

                text = query.message.text if query.message and query.message.text else ''
                answer = await self.generate_fact(text)
                await self.send_response(update, context, answer)
            except Exception as e:
                await self.handle_error(update, context, e)

        elif query.data == 'fact_start':
            self.dialog.set_mode(user_id, 'main')
            dialog_logger.info(f"[{user_id}] Повернення до головного меню (режим main)")
            await start(update, context)

    async def generate_fact(self, user_input: str) -> str:
        dialog_logger.info(f"Виклик GPT з prompt: {self.prompt_key}")
        prompt = load_prompt(self.prompt_key)

        try:
            answer = await chatgpt.send_question(prompt, user_input)
            dialog_logger.info(f"Отримано відповідь GPT ({len(answer)} символів)")
        except Exception as e:
            dialog_logger.error(f"Помилка при запиті до GPT: {e}")
            raise e

        if not answer.strip():
            dialog_logger.warning("GPT повернув порожню відповідь")
            return "На жаль, не вдалося згенерувати факт. Спробуйте ще раз!"

        return answer.strip()

    async def send_response(self, update, context, answer: str):
        dialog_logger.info("Надсилання факту з кнопками")
        await send_text_buttons(update, context, answer, {
            "fact_random": "Ще цікавий факт",
            "fact_start": "Закінчити"
        })

    async def handle_error(self, update, context, error: Exception):
        error_text = f"⚠️ Виникла помилка при генерації факту: {error}"
        await send_text(update, context, error_text)
        log_user_action(update, error_text)
        dialog_logger.exception(f"Помилка в FactGenerator: {error}")


fact_generator = FactGenerator(dialog)

async def random_fact(update, context):
    await fact_generator.handle_command(update, context)

async def button_fact(update, context):
    await fact_generator.handle_button(update, context)
