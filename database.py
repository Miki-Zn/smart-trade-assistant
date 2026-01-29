import aiosqlite
import logging

DB_NAME = "portfolio.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица портфеля
        await db.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ticker TEXT,
                amount REAL,
                avg_price REAL
            )
        """)
        # Таблица уведомлений (Алертов)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                ticker TEXT,
                target_price REAL,
                action_type TEXT
            )
        """)
        await db.commit()

# --- ПОРТФЕЛЬ ---
async def add_portfolio_asset(user_id, ticker, amount, price):
    async with aiosqlite.connect(DB_NAME) as db:
        # Проверяем, есть ли актив
        cursor = await db.execute("SELECT amount, avg_price FROM portfolio WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        row = await cursor.fetchone()
        
        if row:
            # Усреднение
            curr_amt, curr_avg = row
            total_cost = (curr_amt * curr_avg) + (amount * price)
            new_amt = curr_amt + amount
            if new_amt == 0:
                await db.execute("DELETE FROM portfolio WHERE user_id = ? AND ticker = ?", (user_id, ticker))
            else:
                new_avg = total_cost / new_amt
                await db.execute("UPDATE portfolio SET amount = ?, avg_price = ? WHERE user_id = ? AND ticker = ?", (new_amt, new_avg, user_id, ticker))
        else:
            await db.execute("INSERT INTO portfolio (user_id, ticker, amount, avg_price) VALUES (?, ?, ?, ?)", (user_id, ticker, amount, price))
        await db.commit()

async def get_user_portfolio(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM portfolio WHERE user_id = ?", (user_id,))
        return await cursor.fetchall()

async def clear_portfolio(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM portfolio WHERE user_id = ?", (user_id,))
        await db.commit()

# --- АЛЕРТЫ (НОВОЕ) ---
async def add_alert(user_id, ticker, target_price, action_type):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO alerts (user_id, ticker, target_price, action_type) VALUES (?, ?, ?, ?)", 
                         (user_id, ticker, target_price, action_type))
        await db.commit()

async def get_user_alerts(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM alerts WHERE user_id = ?", (user_id,))
        return await cursor.fetchall()

async def get_all_alerts():
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row # Позволяет обращаться по именам колонок
        cursor = await db.execute("SELECT * FROM alerts")
        return await cursor.fetchall()

async def delete_alert(alert_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
        await db.commit()