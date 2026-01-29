# 🤖 AI Financial Ecosystem: Smart Money Agent

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Aiogram](https://img.shields.io/badge/Aiogram-v3-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![OpenAI](https://img.shields.io/badge/GPT--4o-Vision-412991?style=for-the-badge&logo=openai&logoColor=white)
![Tavily](https://img.shields.io/badge/Tavily-Search_API-orange)

**AI Financial Ecosystem** is a next-generation Telegram bot that combines technical and fundamental analysis. The bot acts as two virtual experts: a **Smart Money Trader** and a **Value Investor**.

The system utilizes the multimodal **GPT-4o (Vision & Text)** model for chart analysis and the **Tavily Search API** to gather "hot" news and market insights.

---

## 🚀 Key Features

### 1. 📊 "Trading" Mode (Smart Money Concepts)
Technical asset analysis using computer vision.

* **Input:** Asset Ticker + 3 screenshots (Timeframes: 1D, 4H, 15m).
* **Analysis:**
    * Detection of SMC patterns: *Order Blocks, FVG (Fair Value Gaps), BOS (Break of Structure)*.
    * Analysis of news background and sentiment for the last 24 hours.
* **Risk Management:**
    * Automatic RRR (Risk/Reward Ratio) calculation.
    * ⛔ **Filter:** Trades with RRR < 1:2 are automatically rejected.
* **Result:** Ready-made trading setup (Entry, Stop-Loss, Take-Profit) with reasoning.

### 2. 💼 "Analytics" Mode (Value Investing)
Fundamental company analysis for long-term investing.

* **Input:** Company name or ticker.
* **Analysis:**
    * Deep Web Search: searching for 10-K/10-Q reports, competitor news, lawsuits, and insider sales.
    * Assessment of "Economic Moat" and business model sustainability.
* **Result:**
    * Status: **Undervalued** / **Overvalued**.
    * Strategic targets for buying/selling.

### 🆕 New Features & Updates
* **Modular Architecture:** Transitioned to Routers for better performance.
* **Improved Prompts:** More accurate chart recognition.
* **Database Integration:** SQLite for portfolio tracking.
* **Smart Alerts:** Daily price monitoring via Cron jobs.

---

## 🛠 Tech Stack

* **Language:** Python 3.10+
* **Framework:** `aiogram 3.x` (Fully Asynchronous)
* **AI Core:** OpenAI GPT-4o (Vision + Text Capabilities)
* **Search Engine:** Tavily API (Optimized for LLMs)
* **Database:** `aiosqlite`
* **Environment:** `python-dotenv` for security

---

## 📂 Project Structure

The project is structured for scalability:

```text
smart_money_bot/
├── .env                 # API keys and secrets (do not commit!)
├── .gitignore           # Git exceptions
├── requirements.txt     # Project dependencies
├── main.py              # Entry point
├── config.py            # Configuration and variable loading
├── services.py          # AI and Tavily interaction logic
├── database.py          # Database operations (SQLite)
├── handlers/            # Command and message handlers
└── utils/               # Helper utilities
