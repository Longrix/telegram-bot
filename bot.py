import logging
from flask import Flask
from threading import Thread
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

app = Flask('')

@app.route('/')
def home():
    return "😃Бот-предложка работает!"

def run_flask():
    app.run(host='0.0.0.0',port=8080)

ef keep_alive():
t = Thread(target=run_flask)
t.start()

# === НАСТРОЙКИ БОТА ===
BOT_TOKEN = "8591173518:AAGq6kP0fzGqSPU_Ucd3lQDvnZ0QFu5Pl_A"
CHANNEL_ID = "@ynastakk"  # ЗАМЕНИТЕ НАСТОЯЩИЙ
MODERATION_CHAT_ID = -1003356408124  # ЗАМЕНИТЕ НАСТОЯЩИЙ

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "👋 Привет! Отправляй посты для публикации в канале У нас так! 📝"
    await update.message.reply_text(welcome_text)

# Обработка предложений
async def handle_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = f"📨 От: {user.first_name} (ID: {user.id})"
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Опубликовать", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.copy_message(
            chat_id=MODERATION_CHAT_ID,
            from_chat_id=update.effective_chat.id,
            message_id=update.effective_message.message_id,
            caption=user_info,
            reply_markup=reply_markup
        )
        await update.message.reply_text("✅ Отправлено на модерацию!")
    except Exception as e:
        await update.message.reply_text("❌ Ошибка при отправке")

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = int(data.split('_')[1])
    
    await query.edit_message_reply_markup(reply_markup=None)
    
    if data.startswith('approve'):
        try:
            await context.bot.copy_message(
                chat_id=CHANNEL_ID,
                from_chat_id=MODERATION_CHAT_ID,
                message_id=query.message.message_id
            )
            await query.answer("✅ Опубликовано!")
            try:
                await context.bot.send_message(user_id, "🎉 Ваше предложение опубликовано!")
            except:
                pass
        except Exception as e:
            await query.answer("❌ Ошибка публикации")
    else:
        await query.answer("❌ Отклонено")
        try:
            await context.bot.send_message(user_id, "😔 Ваше предложение отклонено.")
        except:
            pass

# Запуск бота
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, handle_submission))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Бот запущен на Render!")
    application.run_polling()

if __name__ == '__main__':
    main()
