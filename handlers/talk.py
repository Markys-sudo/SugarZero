from utils.util import load_prompt, load_message, send_text, send_text_buttons, send_photo
from utils.logger import log_user_action, logger
from services.dialog import dialog
from services.gpt import chatgpt

class TalkHandler:
    def __init__(self, chatgpt, dialog):
        self.chatgpt = chatgpt
        self.dialog = dialog

    async def talk(self, update, context):
        self.dialog.mode = 'talk'
        msg = load_message('talk')
        await send_photo(update, context, 'talk')
        await send_text_buttons(update, context, msg, {
            'talk_fitness_trainer': 'Фітнес тренер',
            'talk_endocrinologist': 'Ендокринолог',
            'talk_nutritionist': 'Нутриціолог',
            'talk_psychologist': 'Психолог',
        })

    async def talk_button(self, update, context):
        callback = update.callback_query
        query_data = callback.data

        await callback.answer()
        log_user_action(update, f"натиснув кнопку: {query_data}")

        await send_photo(update, context, query_data)
        await send_text(update, context, 'Гарний вибір...')

        prompt = load_prompt(query_data)
        self.chatgpt.set_prompt(prompt)
        self.dialog.mode = 'talk'  # відповідний режим для діалогу

    async def talk_dialog(self, update, context):
        text = update.message.text
        if not text:
            return

        log_user_action(update, f"написав у GPT-діалозі: {text}")

        # Відправка тимчасового повідомлення
        my_msg = await send_text(update, context, '✍️ Набираємо відповідь...')

        try:
            answer = await self.chatgpt.add_message(text)
            # Редагування попереднього повідомлення
            await my_msg.edit_text(answer)
        except Exception as e:
            # Якщо GPT-4o впав — повідомляємо
            await my_msg.edit_text(f"⚠️ Виникла помилка при зверненні до GPT:\n{e}")

talk_handler = TalkHandler(chatgpt, dialog)

async def talk_command(update, context):
    await talk_handler.talk(update, context)

async def talk_button(update, context):
    await talk_handler.callback_handler(update, context)

async def talk_dialog(update, context):
    await talk_handler.talk_dialog(update, context)