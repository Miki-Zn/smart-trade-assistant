import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Получаем ключи
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Проверка наличия ключей
if not BOT_TOKEN:
    raise ValueError("Ошибка: Не найден BOT_TOKEN в файле .env")
if not OPENAI_API_KEY:
    raise ValueError("Ошибка: Не найден OPENAI_API_KEY в файле .env")

# TAVILY нужен для аналитики, но если его нет — выведем предупреждение
if not TAVILY_API_KEY:
    print("Внимание: TAVILY_API_KEY не найден. Поиск новостей работать не будет.")