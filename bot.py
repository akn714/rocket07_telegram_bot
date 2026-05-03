"""Telegram bot (webhook mode) to update Supabase database."""

import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase_client import get_supabase
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = FastAPI()
application = Application.builder().token(BOT_TOKEN).build()


# -------- Commands -------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! Use:\n"
        "/set_delivery_charge <value>\n"
        "/start_orders\n"
        "/close_orders"
    )


async def set_delivery_charge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value = int(float(context.args[0]))
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


async def start_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        supabase = get_supabase()

        supabase.table('config') \
            .update({'is_delivery_closed': False}) \
            .eq('id', 1) \
            .execute()

        await update.message.reply_text("✅ Orders are now OPEN")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def close_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        supabase = get_supabase()

        supabase.table('config') \
            .update({'is_delivery_closed': True}) \
            .eq('id', 1) \
            .execute()

        await update.message.reply_text("🚫 Orders are now CLOSED")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


# -------- Register handlers -------- #

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("set_delivery_charge", set_delivery_charge))
application.add_handler(CommandHandler("start_orders", start_orders))
application.add_handler(CommandHandler("close_orders", close_orders))


# -------- Webhook endpoint -------- #

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/check-alive")
async def check_alive():
    status = {
        "server": "ok"
    }

    # Optional: check Supabase connectivity
    try:
        supabase = get_supabase()
        supabase.table("config").select("*").limit(1).execute()
        status["supabase"] = "ok"
    except Exception as e:
        status["supabase"] = f"error: {str(e)}"

    # Optional: check Telegram bot object exists
    try:
        status["telegram_bot"] = "ok" if application.bot else "not_initialized"
    except Exception as e:
        status["telegram_bot"] = f"error: {str(e)}"

    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)