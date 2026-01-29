import io
import base64
import logging
import yfinance as yf
from openai import AsyncOpenAI
from tavily import TavilyClient
from config import OPENAI_API_KEY, TAVILY_API_KEY

# Инициализация клиентов
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Проверяем ключ Tavily, чтобы бот не падал, если его нет
tavily = None
if TAVILY_API_KEY:
    tavily = TavilyClient(api_key=TAVILY_API_KEY)
else:
    logging.warning("⚠️ Tavily API Key не найден. Поиск новостей работать не будет.")

# ==================================================
# 🛠 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==================================================

def encode_image(image_input):
    """
    Универсальная функция кодирования изображения в base64.
    Принимает:
    1. Путь к файлу (str)
    2. Байты в памяти (io.BytesIO) - то, что приходит от Telegram
    3. Байты (bytes)
    """
    try:
        # Если это путь к файлу (строка)
        if isinstance(image_input, str):
            with open(image_input, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        # Если это объект BytesIO (из Telegram Memory)
        elif isinstance(image_input, io.BytesIO):
            # Перематываем в начало, на случай если файл уже читали
            image_input.seek(0)
            return base64.b64encode(image_input.read()).decode('utf-8')
            
        # Если это просто байты
        elif isinstance(image_input, bytes):
            return base64.b64encode(image_input).decode('utf-8')
            
    except Exception as e:
        logging.error(f"Ошибка кодирования изображения: {e}")
        return None

async def get_live_price(ticker: str):
    """
    Получает актуальную цену актива через Yahoo Finance.
    Используется во всех новых функциях и алертах.
    """
    try:
        clean_ticker = ticker.strip().upper()
        # Для крипты часто нужно добавлять -USD (например BTC-USD), если yfinance не находит
        # Но пока оставим как есть, yfinance умный.
        
        stock = yf.Ticker(clean_ticker)
        
        # Получаем историю за 1 день
        history = stock.history(period="1d")
        
        if not history.empty:
            # Берем цену закрытия последнего бара (это и есть текущая цена или close)
            price = history['Close'].iloc[-1]
            return round(price, 2)
        else:
            logging.warning(f"Не удалось найти цену для {clean_ticker}")
            return 0.0
    except Exception as e:
        print(f"ОШИБКА YFINANCE: {e}") # <-- Добавьте это
        logging.error(f"Ошибка yfinance для {ticker}: {e}")
        return 0.0
# Алиас для старых версий кода (на всякий случай)
get_real_time_price = get_live_price


# ==================================================
# 📊 НОВАЯ ЛОГИКА ТРЕЙДИНГА (3 СКРИНШОТА)
# ==================================================

async def run_trader_analysis(ticker, img_1d, img_4h, img_15m):
    """
    Главная функция для нового main.py.
    Принимает тикер и 3 объекта фото (байты или пути).
    """
    # 1. Получаем реальную цену для контекста
    current_price = await get_live_price(ticker)
    price_str = f"${current_price}" if current_price > 0 else "Цена не найдена"

    # 2. Кодируем все три изображения
    b64_1d = encode_image(img_1d)
    b64_4h = encode_image(img_4h)
    b64_15m = encode_image(img_15m)
    
    if not all([b64_1d, b64_4h, b64_15m]):
        return "❌ Ошибка обработки изображений. Попробуйте снова."

    # 3. Формируем мощный промпт
    prompt = f"""
    Ты профессиональный ICT/SMC Трейдер (Smart Money Concepts).
    Актив: {ticker}. Текущая цена: {price_str}.
    
    Я даю тебе 3 графика этого актива:
    1. Изображение 1: Таймфрейм 1 День (1D) — для определения глобального тренда и Bias.
    2. Изображение 2: Таймфрейм 4 Часа (4H) — для поиска ключевых зон интереса (POI).
    3. Изображение 3: Таймфрейм 15 Минут (15m) — для поиска точки входа (Entry).
    
    ТВОЯ ЗАДАЧА:
    1. **Анализ структуры (Market Structure):** Определи тренд на 1D и 4H. Есть ли слом структуры (BOS/CHoCH)?
    2. **Зоны интереса:** Где находятся Order Blocks (OB), FVG (Imbalance) и пулы ликвидности?
    3. **Сетап:** На основе 15m графика, есть ли точка входа?
    
    ВЫВОД (СТРОГО В ЭТОМ ФОРМАТЕ):
    📈 **Направление:** LONG / SHORT / WAIT (Ждать)
    🚪 **Вход (Entry):** Конкретная цена или зона.
    🛑 **Стоп-лосс (SL):** Цена (Обязательно обоснуй, за какой минимум/максимум).
    💰 **Тейк-профит (TP):** Цена (Ближайшая ликвидность).
    ⚖️ **Risk/Reward:** Рассчитай соотношение. Если < 1:2, напиши ⚠️ ПЛОХОЙ RR.
    
    Пиши кратко, профессионально, используй эмодзи.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_1d}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_4h}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_15m}"}},
                    ],
                }
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка OpenAI (Trader): {e}")
        return f"❌ Ошибка анализа AI: {str(e)}"


# ==================================================
# 🕵️‍♂️ НОВАЯ ЛОГИКА ИНВЕСТОРА (ПОИСК + АНАЛИЗ)
# ==================================================

async def run_investor_analysis(query: str):
    """
    Фундаментальный анализ.
    1. Ищет новости в Tavily.
    2. Берет цену в yfinance.
    3. Анализирует через GPT-4o.
    """
    ticker = query.split()[0].upper() # Пытаемся угадать тикер из первого слова
    
    # 1. Цена
    price = await get_live_price(ticker)
    price_info = f"Текущая цена: ${price}" if price > 0 else "Цена не найдена (возможно, это не тикер, а название)."

    # 2. Поиск новостей
    search_context = "Новости недоступны."
    if tavily:
        try:
            # Ищем свежие данные
            tavily_response = tavily.search(
                query=f"{query} stock financial analysis news forecast 2024 2025 reason to buy or sell",
                search_depth="advanced",
                max_results=6
            )
            # Собираем выжимку
            results = [f"- {r['title']}: {r['content']}" for r in tavily_response.get('results', [])]
            search_context = "\n".join(results)
        except Exception as e:
            logging.error(f"Ошибка Tavily: {e}")
            search_context = f"Ошибка поиска: {e}"

    # 3. Анализ GPT
    prompt = f"""
    Ты Уоррен Баффет и Питер Линч в одном лице.
    Пользователь спрашивает про: "{query}".
    {price_info}
    
    Вот последние данные из интернета:
    {search_context}
    
    ЗАДАЧА:
    1. **Фундаментал:** Что с выручкой, прибылью, долгами? (Если есть в данных).
    2. **Новости:** Позитив или негатив преобладает?
    3. **Риски:** Что может пойти не так?
    4. **Вердикт:**
       - Справедливая цена (примерно).
       - СТАТУС: 🟢 НЕДООЦЕНЕНА / 🔴 ПЕРЕОЦЕНЕНА / 🟡 СПРАВЕДЛИВАЯ ЦЕНА.
    
    Отвечай на русском языке, аргументированно.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Ошибка AI: {e}"


# ==================================================
# 💾 СТАРЫЕ ФУНКЦИИ (LEGACY SUPPORT)
# ==================================================
# Оставлены, чтобы старый код не ломался, если вы решите его использовать.

async def analyze_chart_smc(ticker: str, image_input):
    """
    Старая функция для анализа ОДНОГО графика.
    """
    b64_image = encode_image(image_input)
    if not b64_image:
        return "Ошибка картинки."

    prompt = f"""
    SMC Анализ актива {ticker}.
    Найди Order Blocks, FVG и структуру.
    Дай сигнал: BUY/SELL с уровнями.
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                    ],
                }
            ],
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

async def analyze_fundamental(ticker: str):
    """
    Алиас для run_investor_analysis, чтобы поддерживать старые вызовы.
    """
    return await run_investor_analysis(ticker)


# ==================================================
# 🧠 ПОРТФЕЛЬНЫЙ СОВЕТНИК
# ==================================================

async def get_portfolio_advice_ai(portfolio_text: str):
    """
    Анализирует текстовое описание портфеля и дает советы по балансировке.
    """
    prompt = f"""
    Ты финансовый консультант. Вот портфель клиента:
    {portfolio_text}
    
    1. Оцени диверсификацию (по секторам/риску).
    2. Найди слабые места (например, все в техно, или только крипта).
    3. Посоветуй, что добавить (Золото? Облигации? Китай?).
    
    Кратко, по пунктам.
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка получения совета: {e}"