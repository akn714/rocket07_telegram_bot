"""Telegram bot (webhook mode) to update Supabase database."""

import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from supabase_client import get_supabase
from dotenv import load_dotenv
from datetime import datetime, date, timedelta

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

app = FastAPI()
application = Application.builder().token(BOT_TOKEN).build()


def _is_authorized(update: Update) -> bool:
    chat = update.effective_chat or getattr(update, 'message', None)
    return bool(chat and chat.id == ADMIN_CHAT_ID)


async def _reply_unauthorized(update: Update):
    await update.message.reply_text("⛔ Unauthorized access. This bot is for the admin only.")


# -------- Commands -------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received /start command")
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


async def set_delivery_charge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received /set_delivery_charge command")
    if not _is_authorized(update):
        await _reply_unauthorized(update)
        return

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
    print("Received /start_orders command")
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


async def close_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received /close_orders command")
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
    print("Received /today_orders command")
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


# -------- Register handlers -------- #

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("set_delivery_charge", set_delivery_charge))
application.add_handler(CommandHandler("start_orders", start_orders))
application.add_handler(CommandHandler("close_orders", close_orders))
application.add_handler(CommandHandler("today_orders", today_orders))


# -------- Lifecycle Fix (IMPORTANT) -------- #

@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.start()


@app.on_event("shutdown")
async def shutdown():
    await application.stop()
    await application.shutdown()


# -------- Webhook Endpoint -------- #

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    print(data.get("0"))
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