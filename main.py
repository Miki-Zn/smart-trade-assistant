import asyncio
import io
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import BOT_TOKEN
from services import run_trader_analysis, run_investor_analysis, get_live_price
# Импортируем функции БД
from database import init_db, add_portfolio_asset, get_user_portfolio, clear_portfolio, add_alert, get_user_alerts, delete_alert, get_all_alerts

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler()

# --- КЛАВИАТУРЫ ---

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Трейдинг"), KeyboardButton(text="💼 Аналитика")],
        [KeyboardButton(text="💰 Мой Портфель"), KeyboardButton(text="🔔 Инвест-Советник")],
        [KeyboardButton(text="🧹 Очистить чат")]
    ],
    resize_keyboard=True, persistent=True
)

exit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 В меню", callback_data="menu")]])

# --- СОСТОЯНИЯ (FSM) ---

class TradingState(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_1d = State()
    waiting_for_4h = State()
    waiting_for_15m = State()

class AnalyticsState(StatesGroup):
    waiting_for_ticker = State()

class PortfolioState(StatesGroup):
    ticker = State()
    amount = State()
    price = State()

class AlertState(StatesGroup):
    ticker = State()
    price = State()
    action = State()

# --- ПЛАНИРОВЩИК (9:00 УТРА) ---

async def check_alerts_job():
    """Эта функция запускается каждое утро"""
    logging.info("⏰ Проверка утренних уведомлений...")
    alerts = await get_all_alerts() 
    
    for alert in alerts:
        # alert: id, user_id, ticker, target_price, action_type
        try:
            current_price = await get_live_price(alert['ticker'])
            if current_price == 0: continue

            triggered = False
            msg = ""
            
            # Логика срабатывания
            if alert['action_type'] == 'BUY' and current_price <= alert['target_price']:
                triggered = True
                msg = f"🟢 **СИГНАЛ НА ПОКУПКУ!**\nАкция: {alert['ticker']}\nЦена упала до: {current_price}\nВаша цель: {alert['target_price']}"
            
            elif alert['action_type'] == 'SELL' and current_price >= alert['target_price']:
                triggered = True
                msg = f"🔴 **СИГНАЛ НА ПРОДАЖУ!**\nАкция: {alert['ticker']}\nЦена выросла до: {current_price}\nВаша цель: {alert['target_price']}"
            
            if triggered:
                # Отправляем сообщение пользователю
                await bot.send_message(alert['user_id'], msg)
                # Удаляем выполненную задачу, чтобы не спамить
                await delete_alert(alert['id'])
                
        except Exception as e:
            logging.error(f"Error checking alert {alert['id']}: {e}")

# --- БАЗОВЫЕ КОМАНДЫ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Привет! Я Smart Money Bot v2.0.\nБаза данных подключена.", reply_markup=main_menu_kb)

@dp.message(F.text == "🧹 Очистить чат")
async def cmd_clear(message: types.Message, state: FSMContext):
    await state.clear()
    # Удаляем старую клавиатуру и присылаем новую, создавая эффект "чистого листа"
    msg = await message.answer("🔄", reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    await message.answer("🗑 **Чат и контекст сброшены.**\nНачинаем с чистого листа.", reply_markup=main_menu_kb)

@dp.callback_query(F.data == "menu")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.message.answer("Главное меню:", reply_markup=main_menu_kb)

# ==========================================
# 1. ТРЕЙДИНГ (Smart Money) - ПОЛНЫЙ КОД
# ==========================================

@dp.message(F.text == "📊 Трейдинг")
async def start_trading(msg: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(TradingState.waiting_for_ticker)
    await msg.answer("💹 **Режим Трейдинга**\nВведите Тикер актива:", reply_markup=ReplyKeyboardRemove())

@dp.message(TradingState.waiting_for_ticker)
async def trade_ticker(msg: types.Message, state: FSMContext):
    await state.update_data(ticker=msg.text.upper())
    await msg.answer("📸 Пришли скриншот **1 День (1D)**:")
    await state.set_state(TradingState.waiting_for_1d)

async def download_photo(message: types.Message) -> io.BytesIO:
    # Берем фото лучшего качества
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_content = await bot.download_file(file.file_path)
    return file_content

@dp.message(TradingState.waiting_for_1d, F.photo)
async def trade_1d(message: types.Message, state: FSMContext):
    # Сохраняем ID файла
    await state.update_data(photo_1d=message.photo[-1].file_id)
    await message.answer("📸 Пришли скриншот **4 Часа (4H)**:")
    await state.set_state(TradingState.waiting_for_4h)

@dp.message(TradingState.waiting_for_4h, F.photo)
async def trade_4h(message: types.Message, state: FSMContext):
    await state.update_data(photo_4h=message.photo[-1].file_id)
    await message.answer("📸 Пришли скриншот **15 Минут (15m)**:")
    await state.set_state(TradingState.waiting_for_15m)

@dp.message(TradingState.waiting_for_15m, F.photo)
async def trade_15m(message: types.Message, state: FSMContext):
    data = await state.get_data()
    ticker = data['ticker']
    
    wait_msg = await message.answer("⏳ **Анализирую рынок...**\n(Читаю новости + Сканирую графики)")
    
    try:
        # Скачиваем файлы по ID
        img_1d = await bot.download(data['photo_1d'])
        img_4h = await bot.download(data['photo_4h'])
        img_15m = await bot.download(message.photo[-1].file_id)
        
        # Запуск анализа
        report = await run_trader_analysis(ticker, img_1d, img_4h, img_15m)
        
        await wait_msg.delete()
        # Отправляем отчет с кнопкой выхода
        await message.answer(report, parse_mode="Markdown", reply_markup=exit_kb)
        
    except Exception as e:
        await wait_msg.edit_text(f"❌ Ошибка: {e}")
    
    await state.clear()

# ==========================================
# 2. АНАЛИТИКА (Инвестор)
# ==========================================

@dp.message(F.text == "💼 Аналитика")
async def start_analytics(msg: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(AnalyticsState.waiting_for_ticker)
    await msg.answer("🧐 **Режим Инвестора**\nВведите Тикер или Название компании:", reply_markup=ReplyKeyboardRemove())

@dp.message(AnalyticsState.waiting_for_ticker)
async def analytics_run(msg: types.Message, state: FSMContext):
    wait_msg = await msg.answer("🕵️‍♂️ **Провожу расследование...**\n(Ищу баги, отчеты, инсайды)")
    
    try:
        report = await run_investor_analysis(msg.text)
        await wait_msg.delete()
        await msg.answer(report, parse_mode="Markdown", reply_markup=exit_kb)
    except Exception as e:
        await wait_msg.edit_text(f"❌ Ошибка: {e}")
        
    await state.clear()

# ==========================================
# 3. МОЙ ПОРТФЕЛЬ
# ==========================================

@dp.message(F.text == "💰 Мой Портфель")
async def show_portfolio(msg: types.Message):
    portfolio = await get_user_portfolio(msg.from_user.id)
    
    if not portfolio:
        text = "Ваш портфель пуст."
    else:
        text = "💼 **ВАШ ПОРТФЕЛЬ:**\n\n"
        total_pnl = 0
        
        status_msg = await msg.answer("⏳ Обновляю цены...")
        
        for row in portfolio:
            # row: ticker, amount, avg_price
            live_price = await get_live_price(row['ticker'])
            
            # Считаем PnL
            value_bought = row['amount'] * row['avg_price']
            value_now = row['amount'] * live_price
            pnl = value_now - value_bought
            total_pnl += pnl
            
            emoji = "🟢" if pnl >= 0 else "🔴"
            text += (f"🔹 **{row['ticker']}**\n"
                     f"   {row['amount']} шт | Ср.вход: ${row['avg_price']:.2f}\n"
                     f"   Цена сейчас: ${live_price:.2f}\n"
                     f"   P/L: {emoji} ${pnl:.2f}\n\n")
        
        text += f"💰 **ОБЩИЙ ИТОГ:** ${total_pnl:.2f}"
        await status_msg.delete()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить / Купить", callback_data="port_add")],
        [InlineKeyboardButton(text="➖ Продать / Удалить", callback_data="port_del")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="menu")]
    ])
    await msg.answer(text, reply_markup=kb, parse_mode="Markdown")

# Хендлеры добавления
@dp.callback_query(F.data == "port_add")
async def port_add_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(PortfolioState.ticker)
    await call.message.answer("Введите ТИКЕР (например AAPL):")

@dp.message(PortfolioState.ticker)
async def port_get_ticker(msg: types.Message, state: FSMContext):
    await state.update_data(ticker=msg.text.upper())
    await state.set_state(PortfolioState.amount)
    await msg.answer("Введите КОЛИЧЕСТВО (штук):")

@dp.message(PortfolioState.amount)
async def port_get_amount(msg: types.Message, state: FSMContext):
    try:
        amt = float(msg.text)
        await state.update_data(amount=amt)
        await state.set_state(PortfolioState.price)
        await msg.answer("Введите ЦЕНУ ПОКУПКИ (за 1 шт):")
    except:
        await msg.answer("Ошибка. Введите число.")

@dp.message(PortfolioState.price)
async def port_get_price(msg: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        price = float(msg.text)
        
        # Запись в БД
        await add_portfolio_asset(msg.from_user.id, data['ticker'], data['amount'], price)
        
        await msg.answer(f"✅ {data['ticker']} добавлен!", reply_markup=main_menu_kb)
        await state.clear()
    except:
        await msg.answer("Ошибка. Введите число.")

@dp.callback_query(F.data == "port_del")
async def port_del_start(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Чтобы продать часть, используйте кнопку 'Добавить', но введите количество с минусом (например -5).")

# ==========================================
# 4. ИНВЕСТ-СОВЕТНИК (ALERTS)
# ==========================================

@dp.message(F.text == "🔔 Инвест-Советник")
async def show_alerts(msg: types.Message):
    alerts = await get_user_alerts(msg.from_user.id)
    text = "🔔 **ВАШИ ЗАДАЧИ:**\n\n"
    
    if not alerts:
        text += "Нет активных задач."
    else:
        for a in alerts:
            text += f"📌 **{a['ticker']}** -> Ждем {a['target_price']} ({a['action_type']}) [ID: {a['id']}]\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать задачу", callback_data="alert_create")],
        [InlineKeyboardButton(text="🗑 Удалить по ID", callback_data="alert_delete")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="menu")]
    ])
    await msg.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "alert_create")
async def alert_create(call: CallbackQuery, state: FSMContext):
    await state.set_state(AlertState.ticker)
    await call.message.answer("Введите ТИКЕР для слежки:")

@dp.message(AlertState.ticker)
async def alert_get_ticker(msg: types.Message, state: FSMContext):
    await state.update_data(ticker=msg.text.upper())
    await state.set_state(AlertState.price)
    await msg.answer("Введите ЦЕЛЕВУЮ ЦЕНУ:")

@dp.message(AlertState.price)
async def alert_get_price(msg: types.Message, state: FSMContext):
    try:
        price = float(msg.text)
        await state.update_data(price=price)
        await state.set_state(AlertState.action)
        
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="BUY"), KeyboardButton(text="SELL")]], resize_keyboard=True)
        await msg.answer("Что сделать при достижении цены?", reply_markup=kb)
    except:
        await msg.answer("Введите число.")

@dp.message(AlertState.action)
async def alert_get_action(msg: types.Message, state: FSMContext):
    if msg.text not in ['BUY', 'SELL']:
        await msg.answer("Нажмите кнопку BUY или SELL.")
        return
        
    data = await state.get_data()
    await add_alert(msg.from_user.id, data['ticker'], data['price'], msg.text)
    
    await msg.answer("✅ Задача поставлена! Я проверяю рынок каждое утро в 9:00.", reply_markup=main_menu_kb)
    await state.clear()

@dp.callback_query(F.data == "alert_delete")
async def alert_delete_start(call: CallbackQuery):
    await call.message.answer("Для удаления введите команду: `/del ID` (где ID - номер задачи).")

@dp.message(Command("del"))
async def cmd_del_alert(msg: types.Message):
    try:
        alert_id = int(msg.text.split()[1])
        await delete_alert(alert_id)
        await msg.answer(f"✅ Задача {alert_id} удалена.")
    except:
        await msg.answer("Ошибка. Пример: /del 5")

# --- ЗАПУСК ---
async def main():
    await init_db() # Инициализация базы данных
    
    # Запуск планировщика (каждый день в 9:00)
    scheduler.add_job(check_alerts_job, 'cron', hour=9, minute=0)
    scheduler.start()
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())