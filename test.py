import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Асинхронные обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Выполняется тест бота"
    )

async def handle_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем файл
    file = await update.message.document.get_file()

    # Временная папка
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, "user_file.xlsx")
        await file.download_to_drive(file_path)  # Асинхронное скачивание

        # Читаем Excel
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            await update.message.reply_text(f"Ошибка чтения файла: {e}")
            return

        if df.empty:
            await update.message.reply_text("Файл пуст.")
            return

        # Создаем график
        try:
            plt.figure()
            df.plot()
            plt.title("Данные из Excel")
            plot_path = os.path.join(tmp_dir, "plot.png")
            plt.savefig(plot_path)
            plt.close()

            # Отправляем изображение
            await update.message.reply_photo(photo=open(plot_path, 'rb'))

        except Exception as e:
            await update.message.reply_text(f"Ошибка: {e}")


def main():
    if not TOKEN:
        raise ValueError("Токен не найден в переменных окружения!")

    # Создаем приложение через ApplicationBuilder
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_excel))

    # Запускаем бота
    application.run_polling()

# ================================================= MAIN =================================================

TOKEN = os.environ.get('"TELEGRAM_BOT_TOKEN"')

if __name__ == "__main__":
    main()