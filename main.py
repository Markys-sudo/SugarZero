from telegram.ext import ApplicationBuilder
from config import TOKEN_TG
from handlers.register_handlers import register_all_handlers

def main():
    app = ApplicationBuilder().token(TOKEN_TG).build()

    register_all_handlers(app)

    app.run_polling()

if __name__ == "__main__":
    main()
