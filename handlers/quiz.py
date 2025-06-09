from utils.util import load_prompt, load_message, send_text, send_text_buttons, send_photo
from utils.logger import log_user_action, logger
from database.db import add_quiz_top, get_user_rank
from services.dialog import dialog
from services.gpt import chatgpt

class QuizHandler:
    def __init__(self, chatgpt, dialog, logger):
        self.chatgpt = chatgpt
        self.dialog = dialog
        self.logger = logger

    async def start(self, update, context):
        self.dialog.mode = 'quiz'
        context.user_data['quiz_score'] = 0
        await send_photo(update, context, 'quiz')
        msg = load_message('quiz')
        await send_text_buttons(update, context, msg, {
            'quiz_science': 'Наука і технології',
            'quiz_world': 'Світ навколо нас',
            'quiz_culture': 'Культура та мистецтво',
            'quiz_history': 'Історія та сучасність',
        })

    async def handle_button(self, update, context):
        callback = update.callback_query
        query_data = callback.data
        user = callback.from_user
        user_id = user.id

        self.dialog.mode = 'quiz'

        await callback.answer()  # завжди відповідаємо на callback_query

        log_user_action(update, f"натиснув кнопку: {query_data}")

        if query_data == 'quiz_end':
            score = context.user_data.get('quiz_score', 0)
            add_quiz_top(user, score)
            rank, total = get_user_rank(user.id)
            self.logger.info(f"[{user_id}] Завершив вікторину. Результат: {score}, місце: {rank}/{total}")
            msg = (
                f"🏁 Вікторину завершено.\n"
                f"Ваш результат: {score} правильних відповідей.\n"
                f"📊 Ваш рейтинг: {rank}-е місце з {total} учасників."
            )
            await send_text(update, context, msg)
            return

        # Відправляємо фото без створення нового повідомлення (через send_photo)
        try:
            await send_photo(update, context, query_data)
        except FileNotFoundError:
            await send_text(update, context, "⚠️ Зображення не знайдено.")

        await send_text(update, context, '🎯 Ви обрали категорію. Переходимо до запитань!')

        prompt = load_prompt(query_data)
        context.user_data['quiz_prompt'] = prompt
        context.user_data['quiz_score'] = 0

        await self.ask_new_question(update, context, prompt)

    async def ask_new_question(self, update, context, prompt):
        await send_text(update, context, "❓ Питання готується...")

        raw_question = await self.chatgpt.send_question(
            prompt,
            "Згенеруй одне коротке питання українською мовою з 4 варіантами відповіді та чітко зазнач правильно відповідь. Формат обов’язковий:\n"
            "Питання: ...\nА) ...\nБ) ...\nВ) ...\nГ) ...\nПравильна відповідь: <лише одна літера А/Б/В/Г>"
        )

        parsed = self._parse_question(raw_question)

        if not parsed['question'] or len(parsed['options']) != 4 or not parsed['correct']:
            await send_text(update, context,
                            "⚠️ Сталася помилка при генерації питання. Спробуйте ще раз або оберіть іншу категорію.")
            await self.start(update, context)
            return

        context.user_data['quiz_correct'] = parsed['correct']
        await send_text_buttons(update, context, parsed['question'], {
            **parsed['options'],
            'quiz_end': '🏁 Завершити'
        })

    async def handle_answer(self, update, context):
        callback = update.callback_query
        answer = callback.data
        correct = context.user_data.get('quiz_correct')
        user_id = callback.from_user.id

        await callback.answer()

        if not correct:
            self.logger.warning(f"[{user_id}] Не вдалося перевірити відповідь.")
            await send_text(update, context, "⚠️ Не вдалося перевірити відповідь. Спробуйте ще раз.")
            return

        if answer == correct:
            context.user_data['quiz_score'] += 1
            self.logger.info(f"[{user_id}] ✅ Правильно обрав: {answer}")
            await send_text(update, context, "✅ Вірно!")
        else:
            correct_letter = correct[-1]
            self.logger.info(f"[{user_id}] ❌ Неправильно. Обрав: {answer}, правильно: {correct}")
            await send_text(update, context, f"❌ Невірно. Правильна відповідь: {correct_letter}")

        await send_text(update, context, "📚 Наступне питання готується...")

        prompt = context.user_data.get('quiz_prompt')
        if not prompt:
            await send_text(update, context, "⚠️ Не обрано категорію вікторини. Натисніть /quiz для початку.")
            return

        await self.ask_new_question(update, context, prompt)

    def _parse_question(self, text: str) -> dict:
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        result = {
            'question': '',
            'options': {},
            'correct': ''
        }

        option_map = {'А': 'quiz_A', 'Б': 'quiz_B', 'В': 'quiz_C', 'Г': 'quiz_D'}

        for line in lines:
            if line.lower().startswith("питання:"):
                result['question'] = line.partition(':')[2].strip()
            elif any(line.startswith(f"{k})") for k in option_map):
                prefix = line[0]
                key = option_map.get(prefix)
                result['options'][key] = line[2:].strip()
            elif "правильна відповідь" in line.lower():
                letter = line.strip()[-1].upper()
                result['correct'] = option_map.get(letter, '')

        if not result['question'] or len(result['options']) != 4 or not result['correct']:
            return {'question': '', 'options': {}, 'correct': ''}

        return result

quiz_handler = QuizHandler(chatgpt=chatgpt, dialog=dialog, logger=logger)
# Команда /quiz
async def handle_quiz_command(update, context):
    await quiz_handler.start(update, context)

# Кнопки вибору категорій та завершення
async def handle_quiz_button(update, context):
    await quiz_handler.handle_button(update, context)

# Кнопки відповідей (А/Б/В/Г)
async def handle_quiz_answer(update, context):
    await quiz_handler.handle_answer(update, context)
