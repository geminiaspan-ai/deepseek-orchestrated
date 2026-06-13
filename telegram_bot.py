import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "https://deepseek-orchestrated.onrender.com")  # замени на свой URL

# ========== КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие"""
    await update.message.reply_text(
        "🤖 Привет! Я — голос оркестратора 1 Pro + 9 Flash.\n"
        "Просто отправь мне любой вопрос, и я передам его умной системе.\n\n"
        "⚡ 9 экспертов параллельно подумают над ответом!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    await update.message.reply_text(
        "📖 Как пользоваться:\n"
        "• Отправь текст — получишь ответ от оркестратора\n"
        "• Вопрос может быть любым: от 'как испечь хлеб' до сложной математики\n\n"
        "Команды:\n"
        "/start — приветствие\n"
        "/help — эта справка"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщения — отправка запроса к оркестратору"""
    user_message = update.message.text
    await update.message.reply_chat_action(action="typing")  # Показываем "печатает..."
    
    try:
        # Отправляем запрос к твоему оркестратору
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ORCHESTRATOR_URL}/ask",
                json={"question": user_message},
                timeout=aiohttp.ClientTimeout(total=120)  # 2 минуты на ответ
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    answer = data.get("answer", "Ответ не получен")
                    await update.message.reply_text(answer)
                else:
                    await update.message.reply_text(f"❌ Ошибка API: {resp.status}")
    except asyncio.TimeoutError:
        await update.message.reply_text("⏰ Оркестратор думает слишком долго... Попробуй позже.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

# ========== ЗАПУСК ==========
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
