# 🧠 SugarZero Bot

SugarZero — розумний Telegram-бот, який аналізує фото їжі, визначає інгредієнти та рахує калорійність і БЖУ. Працює на основі GPT-4o та Spoonacular API.

## 🔧 Функціонал

- 📸 Аналіз фото їжі
- 📝 Генерація опису GPT
- 🥦 Визначення інгредієнтів
- 🔥 Підрахунок калорій, білків, жирів, вуглеводів
- 💾 Збереження обраних рецептів
- 🧠 Вікторини по харчуванню та рейтинг користувачів

## 🚀 Запуск локально

1. Клонувати репозиторій:

```bash
git clone https://github.com/Markys-sudo/SugarZero.git
cd SugarZero
```

2. Створити `.env` файл або задати змінні у `config.py`:

```env
TOKEN_TG=your_telegram_bot_token
SPOONACULAR_API=your_spoonacular_api_key
```

3. Встановити залежності:

```bash
pip install -r requirements.txt
```

4. Запустити бота:

```bash
python main.py
```

## 🧠 Архітектура

- `handlers/` — обробники команд та фото
- `services/` — GPT, Spoonacular API, кешування
- `utils/` — логування, утиліти
- `database/bot.db` — SQLite для користувачів, улюбленого та вікторин

## 🛠 Технології

- Python + aiogram/telegram
- OpenAI GPT-4o
- Spoonacular API
- SQLite
- httpx

## 📸 Приклад використання

1. Надішліть боту фото їжі.
2. Отримаєте опис, список інгредієнтів.
3. Бот підрахує калорії та БЖУ.

## 📬 Контакти

Автор: [Markys-sudo](https://github.com/Markys-sudo)  
