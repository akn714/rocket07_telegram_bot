# Telegram Bot for Supabase Updates

- This bot allows updating `delivery_charge` and `is_delivery_closed` in the Supabase database via Telegram commands.
- This is an admin bot used to manage Rocket07 Delivery Service System.
- Rocket07 Delivery System Repo: https://github.com/akn714/online_delivery_system

## Setup

1. Ensure `.env` has the required variables: `TELEGRAM_BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.

2. Run the SQL in `config.sql` to create the configuration table in Supabase.

3. Install dependencies: `pip install python-telegram-bot supabase python-dotenv`

## Running the Bot

```bash
python bot.py
```

## Commands

- `/start`: Welcome message
- `/set_delivery_charge <value>`: Set the delivery charge (e.g., `/set_delivery_charge 5`)
- `/close_orders`: Set delivery closed status as true (closed)
- `/start_orders`: Set delivery closed status as false (start)

The bot updates the row with `id=1` in the `config` table.