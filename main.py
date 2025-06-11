from telegram.ext import ApplicationBuilder
from config import TOKEN_TG
from handlers.register_handlers import register_all_handlers
import logging

logging.basicConfig(
    level=logging.INFO,  # або DEBUG
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
def main():
    app = ApplicationBuilder().token(TOKEN_TG).build()

    register_all_handlers(app)

    app.run_polling()

if __name__ == "__main__":
    main()
