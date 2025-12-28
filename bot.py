import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
from supabase import create_client

# ────────── ENVIRONMENT ────────── #

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ────────── COMMANDS ────────── #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **Broadcast Bot** ✨\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📌 **Commands Menu**\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "➕ ` /add <chat_id> `\n"
        "└ Add channel / group\n\n"
        "➖ ` /remove <chat_id> `\n"
        "└ Remove channel / group\n\n"
        "📃 ` /list `\n"
        "└ Show saved chats\n\n"
        "🚀 *Reply to any message with*\n"
        "` /send `\n"
        "└ Broadcast message\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ Clean • Fast • Modern",
        parse_mode="Markdown"
    )

async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "⚠️ **Usage**\n`/add <chat_id>`",
            parse_mode="Markdown"
        )
        return

    chat_id = int(context.args[0])

    try:
        supabase.table("channels").insert({"id": chat_id}).execute()
        await update.message.reply_text(
            f"✅ **Channel Added**\n\n`{chat_id}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ **Already exists or error occurred**",
            parse_mode="Markdown"
        )
        print(e)

async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "⚠️ **Usage**\n`/remove <chat_id>`",
            parse_mode="Markdown"
        )
        return

    chat_id = int(context.args[0])
    supabase.table("channels").delete().eq("id", chat_id).execute()

    await update.message.reply_text(
        f"❌ **Channel Removed**\n\n`{chat_id}`",
        parse_mode="Markdown"
    )

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = supabase.table("channels").select("*").execute().data

    if not data:
        await update.message.reply_text(
            "📭 **No channels saved yet**",
            parse_mode="Markdown"
        )
        return

    text = "📢 **Saved Channels**\n\n"
    for row in data:
        text += f"• `{row['id']}`\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ **Reply to a message with** `/send`",
            parse_mode="Markdown"
        )
        return

    channels = supabase.table("channels").select("*").execute().data
    original_message = update.message.reply_to_message

    success = 0
    failed = 0

    for row in channels:
        try:
            await original_message.copy(chat_id=row["id"])
            success += 1
        except Exception as e:
            failed += 1
            print(f"Failed → {row['id']} | {e}")

    await update.message.reply_text(
        "📊 **Broadcast Report**\n\n"
        f"✅ Success : `{success}`\n"
        f"❌ Failed  : `{failed}`",
        parse_mode="Markdown"
    )

# ────────── MAIN ────────── #

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_channel))
    app.add_handler(CommandHandler("remove", remove_channel))
    app.add_handler(CommandHandler("list", list_channels))
    app.add_handler(CommandHandler("send", handle_send))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
