# 📊 Telegram Group Engagement Bot

A Python-based Telegram bot that tracks chat activity and generates visual performance reports. Built with `aiogram`, `matplotlib`, and `aiosqlite`.

## ✨ Features
- **Auto-Tracking:** Saves message counts and timestamps for every user.
- **Visual Dashboard:** Use `/stats` to get a custom-generated image containing:
  - 🥧 **Pie Chart:** Showing the percentage of activity per top user.
  - 📊 **Bar Chart:** Showing the busiest hours of the day (UTC).
- **Leaderboard:** A text-based top 5 list with medals (🥇🥈🥉).

## 🛠️ Installation & Setup

### 1. Requirements
You will need Python installed. Install the necessary libraries using:
```bash
pip install aiogram aiosqlite matplotlib python-dotenv
