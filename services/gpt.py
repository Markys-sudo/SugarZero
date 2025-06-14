from config import  PROXY_GPT, TOKEN_GPT
from openai import AsyncOpenAI
import httpx
import base64
import mimetypes

MODEL_GPT = "gpt-4o"

shared_http_client = httpx.AsyncClient(proxy=PROXY_GPT)

class ChatGptService:
    def __init__(self, token: str):
        if not token:
            raise ValueError("❌ TOKEN_GPT не встановлено. Перевір .env або Railway Variables")

        self.client = AsyncOpenAI(
            api_key=token,
            http_client=shared_http_client,
        )
        self.message_list = []

    async def ask(self, prompt: str) -> str:
        return await self.send_question("", prompt)

    async def translate_text(self, text, target_language='en'):
        prompt = f"Переклади цей текст на {target_language.upper()} мовою без пояснень:\n{text}"
        return await self.ask(prompt)

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def send_message_list(self) -> str:
        response = await self.client.chat.completions.create(
            model=MODEL_GPT,
            messages=self.message_list,
            max_tokens=3000,
            temperature=0.9
        )
        message = response.choices[0].message
        # self.message_list.append(message)
        return message.content

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        reply = await self.send_message_list()
        self.message_list.append({"role": "assistant", "content": reply})
        return reply

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list = [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": message_text}
        ]
        return await self.send_message_list()

    async def describe_image(self, file_path: str,
                             prompt: str = "Опиши, що зображено на цьому фото українською мовою.") -> str:
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "image/jpeg"

            with open(file_path, "rb") as img_file:
                b64_data = base64.b64encode(img_file.read()).decode("utf-8")

            response = await self.client.chat.completions.create(
                model=MODEL_GPT,
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_data}"}}
                    ]}
                ],
                max_tokens=800,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Помилка при описі зображення: {e}"

        return response.choices[0].message.content

# Ініціалізація глобального екземпляра GPT
chatgpt = ChatGptService(token=TOKEN_GPT)