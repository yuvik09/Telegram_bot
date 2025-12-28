import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Yaha channel IDs daalna (bot admin hona chahiye)
CHANNEL_IDS = [
    -1002953344164,
    -1003668350192,
    -1003589130945,
    -1003531245130
]

async def handle_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Kisi message ko reply karke /send likho")
        return

    original_message = update.message.reply_to_message

    for channel_id in CHANNEL_IDS:
        try:
            await original_message.copy(chat_id=channel_id)
        except Exception as e:
            print(f"Error sending to {channel_id}: {e}")

    await update.message.reply_text("✅ Message sab channels me bhej diya")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot ready hai")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", handle_send))

    app.run_polling()

if __name__ == "__main__":
    main()
