"""Telegram bot to update Supabase database."""

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase_client import get_supabase
from dotenv import load_dotenv
from datetime import datetime, date, timedelta

load_dotenv()

# Get bot token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

def _is_authorized(update: Update) -> bool:
    chat = update.effective_chat or getattr(update, 'message', None)
    return bool(chat and chat.id == ADMIN_CHAT_ID)


async def _reply_unauthorized(update: Update):
    await update.message.reply_text("⛔ Unauthorized access. This bot is for the admin only.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not _is_authorized(update):
        await _reply_unauthorized(update)
        return

    await update.message.reply_text(
        "Hi! Use:\n"
        "/set_delivery_charge <value>\n"
        "/start_orders\n"
        "/close_orders\n"
        "/today_orders"
    )


async def set_delivery_charge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Update delivery_charge in the database."""
    if not _is_authorized(update):
        await _reply_unauthorized(update)
        return

    try:
        value = int(float(context.args[0]))  # handles decimals too
        supabase = get_supabase()

        supabase.table('config') \
            .update({'delivery_charge': value}) \
            .eq('id', 1) \
            .execute()

        await update.message.reply_text(f"✅ Delivery charge updated to {value}")

    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /set_delivery_charge <number>")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def start_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set is_delivery_closed = False (orders open)."""
    if not _is_authorized(update):
        await _reply_unauthorized(update)
        return

    try:
        supabase = get_supabase()

        supabase.table('config') \
            .update({'is_delivery_closed': False}) \
            .eq('id', 1) \
            .execute()

        await update.message.reply_text("✅ Orders are now OPEN")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def close_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set is_delivery_closed = True (orders closed)."""
    if not _is_authorized(update):
        await _reply_unauthorized(update)
        return

    try:
        supabase = get_supabase()

        supabase.table('config') \
            .update({'is_delivery_closed': True}) \
            .eq('id', 1) \
            .execute()

        await update.message.reply_text("🚫 Orders are now CLOSED")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def today_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_authorized(update):
        await _reply_unauthorized(update)
        return

    try:
        supabase = get_supabase()

        today = date.today()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today + timedelta(days=1), datetime.min.time())

        response = supabase.table('orders').select('*').gte('created_at', start.isoformat()).lt('created_at', end.isoformat()).execute()
        orders = response.data

        if not orders:
            await update.message.reply_text("No orders placed today.")
            return

        message = ""
        for order in orders:
            message += f"Name: {order['name']}\n"
            message += f"Phone No. {order['phone']}\n"
            message += f"Hostel: {order['address']}\n"
            message += f"Total Amount: {order['total_price']}\n"
            message += f"OTP: {order['otp']}\n"
            message += "Products:\n"
            for item in order['items']:
                message += f"- {item}\n"
            message += "\n----------------------------------------------\n"

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_delivery_charge", set_delivery_charge))
    application.add_handler(CommandHandler("start_orders", start_orders))
    application.add_handler(CommandHandler("close_orders", close_orders))
    application.add_handler(CommandHandler("today_orders", today_orders))

    application.run_polling()


if __name__ == "__main__":
    main()