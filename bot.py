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
OWNER_ID = int(os.environ.get("OWNER_ID"))  # Your Telegram ID

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ────────── HELPER ────────── #

def is_owner(update: Update) -> bool:
    """Check if user is the bot owner."""
    return update.effective_user.id == OWNER_ID

async def owner_only(update: Update, context: ContextTypes.DEFAULT_TYPE, command_name: str):
    """Send warning if non-owner tries owner-only command."""
    await update.message.reply_text(
        f"❌ You are not authorized to use `{command_name}`",
        parse_mode="Markdown"
    )

# ────────── COMMANDS ────────── #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean, modern start message (everyone can use)."""
    text = (
        "✨ *Broadcast Bot* ✨\n\n"
        "📌 *Available Commands:*\n\n"
        "➕ `/add <chat_id>` — Add a channel/group (Owner only)\n"
        "➖ `/remove <chat_id>` — Remove a channel/group (Owner only)\n"
        "🧹 `/remove_all` — Remove ALL channels (Owner only)\n"
        "📃 `/list` — Show all saved channels\n"
        "🚀 Reply to any message with `/send` to broadcast"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await owner_only(update, context, "/add")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/add <chat_id>`", parse_mode="Markdown")
        return

    chat_id = int(context.args[0])
    try:
        supabase.table("channels").insert({"id": chat_id}).execute()
        await update.message.reply_text(f"✅ Channel added: `{chat_id}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text("❌ Already exists or error occurred", parse_mode="Markdown")
        print(e)

async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await owner_only(update, context, "/remove")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/remove <chat_id>`", parse_mode="Markdown")
        return

    chat_id = int(context.args[0])
    supabase.table("channels").delete().eq("id", chat_id).execute()
    await update.message.reply_text(f"❌ Channel removed: `{chat_id}`", parse_mode="Markdown")

async def remove_all_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await owner_only(update, context, "/remove_all")
        return

    supabase.table("channels").delete().neq("id", 0).execute()
    await update.message.reply_text("🧹 All channels removed successfully", parse_mode="Markdown")

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await owner_only(update, context, "/list")
        return

    data = supabase.table("channels").select("*").execute().data
    if not data:
        await update.message.reply_text("📭 No channels saved yet", parse_mode="Markdown")
        return

    text = "📢 *Saved Channels:*\n"
    for row in data:
        text += f"• `{row['id']}`\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def handle_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await owner_only(update, context, "/send")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Reply to a message with `/send` to broadcast", parse_mode="Markdown")
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
        "📊 *Broadcast Report*\n\n"
        f"✅ Success: `{success}`\n"
        f"❌ Failed: `{failed}`",
        parse_mode="Markdown"
    )

# ────────── MAIN ────────── #

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_channel))
    app.add_handler(CommandHandler("remove", remove_channel))
    app.add_handler(CommandHandler("remove_all", remove_all_channels))
    app.add_handler(CommandHandler("list", list_channels))
    app.add_handler(CommandHandler("send", handle_send))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
