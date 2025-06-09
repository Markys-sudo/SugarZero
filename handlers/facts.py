from services.dialog import dialog
from services.gpt import chatgpt
from utils.util import load_prompt, send_text_buttons, send_text, send_photo
from utils.logger import log_user_action
from handlers.main_menu import start


class FactGenerator:
    def __init__(self, dialog):
        self.dialog = dialog
        self.prompt_key = "random_fact"

#обробка команди /random (або іншої, яка запускає генерацію факту).
    async def handle_command(self, update, context):
        text = update.message.text if update.message and update.message.text else ''
        log_user_action(update, f"написав: {text}")
        self.dialog.mode = 'random_fact'

        await send_photo(update, context, 'fact')

        try:
            answer = await self.generate_fact(text)
            await self.send_response(update, context, answer)
        except Exception as e:
            await self.handle_error(update, context, e)

#обробка натискань кнопок у відповіді.
    async def handle_button(self, update, context):
        query = update.callback_query
        await query.answer()
        log_user_action(update, f"натиснув кнопку: {query.data}")

        if query.data == 'fact_random':
            try:
                text = query.message.text if query.message and query.message.text else ''
                answer = await self.generate_fact(text)
                await self.send_response(update, context, answer)
            except Exception as e:
                await self.handle_error(update, context, e)

        elif query.data == 'fact_start':
            await start(update, context)

#виклик GPT через свій сервіс.
    async def generate_fact(self, user_input: str) -> str:
        prompt = load_prompt(self.prompt_key)
        return await chatgpt.send_question(prompt, user_input)

#надсилання тексту з кнопками.
    async def send_response(self, update, context, answer: str):
        await send_text_buttons(update, context, answer, {
            "fact_random": "Ще цікавий факт",
            "fact_start": "Закінчити"
        })

# обробка помилок і логування.
    async def handle_error(self, update, context, error: Exception):
        error_text = f"⚠️ Виникла помилка при генерації факту: {error}"
        await send_text(update, context, error_text)
        log_user_action(update, f" — {error_text}")


fact_generator = FactGenerator(dialog)

async def random_fact(update, context):
    await fact_generator.handle_command(update, context)

async def button_fact(update, context):
    await fact_generator.handle_button(update, context)