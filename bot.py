"""Telegram bot to update Supabase database."""

import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase_client import get_supabase
from dotenv import load_dotenv

load_dotenv()

# Get bot token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Hi! Use:\n"
        "/set_delivery_charge <value>\n"
        "/start_orders\n"
        "/close_orders"
    )


async def set_delivery_charge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Update delivery_charge in the database."""
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
    try:
        supabase = get_supabase()

        supabase.table('config') \
            .update({'is_delivery_closed': True}) \
            .eq('id', 1) \
            .execute()

        await update.message.reply_text("🚫 Orders are now CLOSED")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_delivery_charge", set_delivery_charge))
    application.add_handler(CommandHandler("start_orders", start_orders))
    application.add_handler(CommandHandler("close_orders", close_orders))

    application.run_polling()


if __name__ == "__main__":
    main()