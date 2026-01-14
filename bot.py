import asyncio
import logging
import os
import aiosqlite
import io
import matplotlib.pyplot as plt
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# --- 1. CONFIGURATION ---
BOT_TOKEN = "8545441860:AAHXh3B2_HDbJKbkHNrIAEunJvEhyx7zuSU"

# Database path setup
DB_FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "tg_engagement_db")
os.makedirs(DB_FOLDER, exist_ok=True)
DB = os.path.join(DB_FOLDER, "engagement.db")

# Initialize Bot and Dispatcher (Fixes NameError: 'dp')
bot = Bot(token=BOT_TOKEN)
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

# --- 3. THE STATS COMMAND (Visuals + Leaderboard) ---
@dp.message(Command("stats"))
async def stats(message: types.Message):
    group_name = message.chat.title if message.chat.title else "this group"
    
    async with aiosqlite.connect(DB) as db:
        # Fetch Top Contributors
        cursor_share = await db.execute("""
            SELECT username, COUNT(*) FROM messages 
            WHERE chat_id = ? GROUP BY user_id 
            ORDER BY COUNT(*) DESC LIMIT 5
        """, (message.chat.id,))
        share_rows = await cursor_share.fetchall()

        # Fetch Hourly Activity
        cursor_hours = await db.execute("""
            SELECT strftime('%H', timestamp) as hour, COUNT(*) 
            FROM messages WHERE chat_id = ? 
            GROUP BY hour ORDER BY hour ASC
        """, (message.chat.id,))
        hour_rows = await cursor_hours.fetchall()

    if not share_rows:
        await message.reply("No data yet! Send some messages first.")
        return

    # --- 1. Leaderboard Text (Names and Medals) ---
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    leaderboard_text = f"📊 **Activity Report: {group_name}**\n\n"
    leaderboard_text += "🔥 **Top Contributors:**\n"
    
    for i, (username, count) in enumerate(share_rows):
        rank_icon = medals[i] if i < len(medals) else f"{i+1}."
        user_display = f"@{username}" if username != "unknown" else "User"
        leaderboard_text += f"{rank_icon} {user_display}: **{count} messages**\n"

    # --- 2. White Background Visuals (Matching your photo) ---
    plt.figure(figsize=(10, 5))
    plt.style.use('default') # Forces white background style
    
    # Left: Pie Chart (Matching Blue, Green, Purple colors)
    plt.subplot(1, 2, 1)
    labels = [f"@{r[0]}" if r[0] != "unknown" else "User" for r in share_rows]
    colors = ['#4dd2ff', '#99e699', '#ac71db', '#ffdb4d', '#ff944d']
    plt.pie([r[1] for r in share_rows], labels=labels, autopct='%1.1f%%', 
            startangle=140, colors=colors)
    plt.title("Top Contributors", fontsize=10)

    # Right: Orange Bar Chart
    plt.subplot(1, 2, 2)
    hours_dict = {int(r[0]): r[1] for r in hour_rows}
    y_values = [hours_dict.get(h, 0) for h in range(24)]
    plt.bar(range(24), y_values, color='#f0a041', width=0.8) 
    plt.title("Busiest Hours (UTC)", fontsize=10)
    plt.xlabel("Hour in Day", fontsize=8)
    plt.xticks(range(0, 24, 6), fontsize=8)

    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='white')
    buf.seek(0)
    plt.close()

    # --- 3. Final Output ---
    photo = types.BufferedInputFile(buf.getvalue(), filename="dashboard.png")
    await message.answer_photo(
        photo=photo, 
        caption=leaderboard_text,
        parse_mode="Markdown"
    )

# --- 4. MESSAGE TRACKER ---
@dp.message()
async def track_message(message: types.Message):
    if message.text and message.text.startswith('/'):
        return
    
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
            INSERT INTO messages (user_id, username, chat_id, timestamp) 
            VALUES (?, ?, ?, ?)
        """, (
            message.from_user.id, 
            message.from_user.username or "unknown", 
            message.chat.id, 
            datetime.now(timezone.utc).isoformat()
        ))
        await db.commit()

# --- 5. RUN THE BOT ---
async def main():
    await init_db()
    print("🤖 Bot is live! Press Ctrl+C to stop.")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nBot stopped safely.")