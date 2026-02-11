import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from database import init_db, save_message, get_messages_today
from summarizer import summarize_messages

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I am your Telegram Assistant Bot.\n"
        "I will read messages in this group and can summarize them for you.\n"
        "Commands:\n"
        "/reminder - Remind users to report\n"
        "/report - Generate a summary of today's messages"
    )

async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📢 **Daily Reminder!**\n\n"
        "Please update your status and report any important progress for the day. "
        "Don't forget to mention any blockers!"
    )

    
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title or "Private Chat"
    await update.message.reply_text(f"Chat ID for '{chat_title}': `{chat_id}`", parse_mode='Markdown')

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Default to current chat
    target_chat_id = update.effective_chat.id
    target_name = "Current Chat"

    # Check for arguments (e.g., /report bd, /report mkt)
    if context.args and len(context.args) > 0:
        arg = context.args[0].lower()
        if arg == 'bd':
            bd_id = os.getenv("BD_CHAT_ID")
            if bd_id:
                target_chat_id = int(bd_id)
                target_name = "BD Group"
            else:
                await update.message.reply_text("⚠️ BD_CHAT_ID not set in configuration.")
                return
        elif arg == 'mkt':
            mkt_id = os.getenv("MKT_CHAT_ID")
            if mkt_id:
                target_chat_id = int(mkt_id)
                target_name = "Marketing Group"
            else:
                await update.message.reply_text("⚠️ MKT_CHAT_ID not set in configuration.")
                return

    print(f"DEBUG: Generating report for {target_name} ({target_chat_id})")
    
    # Determine group type based on chat ID or explicit target name
    bd_id_env = os.getenv("BD_CHAT_ID")
    if target_name == "BD Group" or (bd_id_env and str(target_chat_id) == bd_id_env):
        group_type = 'bd'
    else:
            group_type = 'default'

    # Notify user we are syncing/processing
    status_msg = await update.message.reply_text("🔄 Syncing latest messages...")
    
    # Simulate sync delay to ensure all pending updates are processed
    # In reality, the bot receives updates in real-time, but this ensures the event loop has cycled
    await asyncio.sleep(2) 

    messages = get_messages_today(target_chat_id)
    
    # Update status to generating
    await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=status_msg.message_id, text="📝 Generating report...")

    summary = await summarize_messages(messages, group_type)
    print(f"DEBUG: Summary generated. Length: {len(summary)}")
    print(f"DEBUG: Summary content prefix: {summary[:100]}...")
    
    try:
        # Delete status message
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=status_msg.message_id)
        await update.message.reply_text(f"📝 <b>Daily Summary Report ({target_name})</b>:\n\n{summary}", parse_mode='HTML')
    except Exception as e:
        print(f"ERROR: Failed to send HTML report: {e}")
        await update.message.reply_text(f"⚠️ HTML Parsing Failed. Sending raw text:\n\n{summary}")

async def report_bd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shortcut for /report bd"""
    # Manually simulate arguments for the report function
    context.args = ['bd']
    await report(update, context)

async def report_mkt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shortcut for /report mkt"""
    # Manually simulate arguments for the report function
    context.args = ['mkt']
    await report(update, context)

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from datetime import datetime
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    debug_info = f"🛠 **Debug Info**\n"
    debug_info += f"Current Chat ID: `{chat_id}` ({chat_type})\n"
    debug_info += f"Server Time: `{datetime.now()}`\n"
    
    # 1. Check messages for CURRENT chat
    messages = get_messages_today(chat_id)
    msg_count = len(messages)
    debug_info += f"Messages in THIS chat today: {msg_count}\n"

    # 2. If Private chat, ALSO check the configured MKT Group
    if chat_type == 'private':
        mkt_group_id = os.getenv("MKT_CHAT_ID")
        if mkt_group_id:
            try:
                mkt_id = int(mkt_group_id)
                mkt_msgs = get_messages_today(mkt_id)
                debug_info += f"\n📊 **MKT Group Stats ({mkt_id})**:\n"
                debug_info += f"Messages Today: {len(mkt_msgs)}\n"
                if len(mkt_msgs) > 0:
                    last_msg = mkt_msgs[-1]
                    debug_info += f"Last Msg: `{last_msg[1][:20]}...` at `{last_msg[2]}`\n"
            except ValueError:
                debug_info += f"\n⚠️ Invalid MKT_CHAT_ID format: {mkt_group_id}\n"
        else:
            debug_info += "\n⚠️ MKT_CHAT_ID not set in .env\n"
            
    if msg_count > 0:
        last_msg = messages[-1]
        debug_info += f"\nLast Msg in THIS chat: `{last_msg[1][:20]}...` at `{last_msg[2]}`"
    
    await update.message.reply_text(debug_info, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # DEBUG: Print everything received
    print(f"DEBUG: Received update: {update}")

    if not update.message or not update.message.text:
        return

    user = update.effective_user
    chat = update.effective_chat
    
    username = user.username or user.first_name
    chat_title = chat.title or "Private"
    
    # Use datetime.now() for local time storage to match get_messages_today logic
    from datetime import datetime
    save_message(
        user_id=user.id,
        username=username,
        chat_id=chat.id,
        chat_title=chat_title,
        content=update.message.text,
        timestamp=datetime.now()
    )
    print(f"Saved message from {username} in {chat_title}: {update.message.text[:20]}...")

def main():
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    init_db()
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    reminder_handler = CommandHandler('reminder', reminder)
    report_handler = CommandHandler('report', report)
    bd_handler = CommandHandler('bd', report_bd)
    mkt_handler = CommandHandler('mkt', report_mkt)
    debug_handler = CommandHandler('debug', debug)
    chat_id_handler = CommandHandler('chatId', get_chat_id)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(reminder_handler)
    application.add_handler(report_handler)
    application.add_handler(bd_handler)
    application.add_handler(mkt_handler)
    application.add_handler(debug_handler)
    application.add_handler(chat_id_handler)
    application.add_handler(message_handler)
    
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
