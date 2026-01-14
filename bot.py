import asyncio
import logging
import os
import aiosqlite
import io
import matplotlib.pyplot as plt
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file!")

# Database path setup
DB_FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "tg_engagement_db")
os.makedirs(DB_FOLDER, exist_ok=True)
DB = os.path.join(DB_FOLDER, "engagement.db")

# Initialize Bot and Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- 2. DATABASE INITIALIZATION ---
async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            chat_id INTEGER,
            timestamp TEXT
        )
        """)
        await db.commit()
    print("✅ Database is ready.")

# --- 3. THE STATS COMMAND ---
@dp.message(Command("stats"))
async def stats(message: types.Message):
    async with aiosqlite.connect(DB) as db:
        # Fetch Top Contributors
        cursor_share = await db.execute("""
            SELECT username, COUNT(*) FROM messages 
            WHERE chat_id = ? GROUP BY user_id 
            ORDER BY COUNT(*) DESC LIMIT 5
        """, (message.chat.id,))
        share_rows = await cursor_share.fetchall()

    if not share_rows:
        await message.reply("No data yet! Send some regular messages first.")
        return

    leaderboard_text = f"📊 Activity Report\n\n🔥 Top Contributors:\n"
    for i, (username, count) in enumerate(share_rows):
        user_display = f"@{username}" if username else "User"
        leaderboard_text += f"{i+1}. {user_display}: {count} messages\n"

    await message.answer(leaderboard_text)

# --- 4. MESSAGE TRACKER ---
@dp.message()
async def track_message(message: types.Message):
    # This part was missing in your code! 
    if message.text and message.text.startswith('/'):
        return
    
    # This prints to your CMD so you can see it working
    print(f"📥 Tracking message from: {message.from_user.username}")

    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO messages (user_id, username, chat_id, timestamp)
            VALUES (?, ?, ?, ?)
        """, (message.from_user.id, message.from_user.username, message.chat.id, datetime.now(timezone.utc).isoformat()))
        await db.commit()

# --- 5. RUN THE BOT ---
async def main():
    await init_db()
    print("Bot is starting...")
    await dp.start_polling(bot)

# Fixed the underscores here
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
