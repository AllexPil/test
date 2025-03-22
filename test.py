import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

class Plots:
    def __init__(self, df, plt, pdf):
        self.df = df
        self.plt = plt
        self.pdf = pdf
        self.create_pdf()

    def create_pdf(self):
        for i in range(5):
            self.plot()
            self.pdf.savefig()
            self.plt.close()

    def plot(self):
        self.df.plot()
        self.plt.title("Данные из Excel")


class Stars_bot:
    def __init__(self, TOKEN):
        # Создаем приложение через ApplicationBuilder
        application = ApplicationBuilder().token(TOKEN).build()

        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.Document.ALL, self.handle_excel))

        # Запускаем бота
        application.run_polling()
    @staticmethod
    # Асинхронные обработчики
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Привет! Отправьте мне файл Excel (.xlsx), и я сгенерирую для вас диаграммы."
        )

    @staticmethod
    async def handle_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Получаем файл
        file = await update.message.document.get_file()

        # Временная папка
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = os.path.join(tmp_dir, "user_file.xlsx")
            await file.download_to_drive(file_path)  # Асинхронное скачивание

            # Читаем Excel
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                await update.message.reply_text(f"Ошибка чтения файла: {e}")
                return

            if df.empty:
                await update.message.reply_text("Файл пуст.")
                return

            # Создаем график
            try:
                os.makedirs('tmp_dir', exist_ok=True)
                pdf = PdfPages('tmp_dir/Diagrams.pdf')

                plt.figure(figsize=(16, 10))

                Plots(df, plt, pdf)

                pdf.close()

                # Отправляем изображение
                await update.message.reply_document(document=open('tmp_dir/Diagrams.pdf', 'rb'))

                os.remove('tmp_dir/Diagrams.pdf')
                os.rmdir('tmp_dir')

            except Exception as e:
                await update.message.reply_text(f"Ошибка: {e}")

# ================================================= MAIN =================================================

if __name__ == "__main__":
    Stars_bot(TOKEN)
