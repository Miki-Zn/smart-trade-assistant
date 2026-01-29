# 🤖 AI Financial Ecosystem: Trader & Analyst Bot

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Aiogram](https://img.shields.io/badge/aiogram-v3.x-blueviolet?logo=telegram)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green?logo=openai)
![Tavily](https://img.shields.io/badge/Tavily-Search_API-orange)

**AI Financial Ecosystem** — это комплексный Telegram-бот нового поколения, объединяющий технический и фундаментальный анализ. Бот выступает в роли двух виртуальных экспертов: **Smart Money Трейдера** и **Value Инвестора**.

Система использует мультимодальную модель **GPT-4o (Vision & Text)** для анализа графиков и **Tavily Search API** для сбора "горячих" новостей и инсайдов.

---

## 🚀 Основные возможности

### 1. 📊 Режим "Трейдинг" (Smart Money Concept)
Технический анализ активов с использованием компьютерного зрения.

* **Вход:** Тикер актива + 3 скриншота (Таймфреймы: 1D, 4H, 15m).
* **Анализ:**
    * Поиск SMC паттернов: *Order Blocks, FVG (Fair Value Gaps), BOS (Break of Structure)*.
    * Анализ новостного фона и сентимента за последние 24 часа.
* **Риск-менеджмент:**
    * Автоматический расчет RRR (Risk/Reward Ratio).
    * ⛔ **Фильтр:** Сделки с RRR < 1:2 автоматически отклоняются.
* **Результат:** Готовый торговый сетап (Entry, Stop-Loss, Take-Profit) с аргументацией.

### 2. 💼 Режим "Аналитика" (Value Investing)
Фундаментальный анализ компаний для долгосрочного инвестирования.

* **Вход:** Название компании или тикер.
* **Анализ:**
    * Deep Web Search: поиск отчетов 10-K/10-Q, новостей о конкурентах, судебных исках и инсайдерских продажах.
    * Оценка "Экономического рва" (Moat) и устойчивости бизнес-модели.
* **Результат:**
    * Статус: **Undervalued** (Недооценен) / **Overvalued** (Переоценен).
    * Стратегические цели для покупки/продажи.

### 🆕 Новые функции и обновления
* **Модульная архитектура:** Переход на роутеры (Routers) для лучшей производительности.
* **Улучшенные промпты:** Более точное распознавание графиков.
* *(Добавьте сюда свои новые функции, например: Подключение БД, Админ-панель и т.д.)*

---

## 🛠 Технический стек

* **Язык:** Python 3.10+
* **Фреймворк:** `aiogram 3.x` (Полностью асинхронный)
* **AI Core:** OpenAI GPT-4o (Vision + Text Capabilities)
* **Search Engine:** Tavily API (Optimized for LLMs)
* **Environment:** `python-dotenv` для безопасности

---

## 📂 Структура проекта

Проект обновлен для поддержки масштабируемости:

```text
smart_money_bot/
├── .env                 # API ключи и секреты (не коммитить!)
├── .gitignore           # Исключения для Git
├── requirements.txt     # Зависимости проекта
├── main.py              # Точка входа (Entry point)
├── config.py            # Конфигурация и загрузка переменных
├── services.py          # Логика взаимодействия с AI и Tavily
├── handlers/            # [NEW] Обработчики команд и сообщений
│   ├── __init__.py
│   ├── user_commands.py # Команды /start, /help
│   └── analysis.py      # Логика приема фото и тикеров
├── keyboards/           # [NEW] Клавиатуры и кнопки
│   └── builders.py
└── utils/               # [NEW] Вспомогательные утилиты

Поскольку вы не прикрепили код самих новых файлов, я составил обновленный README.md, предполагая, что под «новыми файлами» подразумевается модульная структура (стандартная практика для aiogram 3.x при расширении проекта).

Я разбил структуру на логические модули (handlers, keyboards, callbacks) и добавил разделы для новых функций.

Вы можете скопировать этот код и сохранить его как README.md.

Markdown

# 🤖 AI Financial Ecosystem: Trader & Analyst Bot

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![Aiogram](https://img.shields.io/badge/aiogram-v3.x-blueviolet?logo=telegram)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green?logo=openai)
![Tavily](https://img.shields.io/badge/Tavily-Search_API-orange)

**AI Financial Ecosystem** — это комплексный Telegram-бот нового поколения, объединяющий технический и фундаментальный анализ. Бот выступает в роли двух виртуальных экспертов: **Smart Money Трейдера** и **Value Инвестора**.

Система использует мультимодальную модель **GPT-4o (Vision & Text)** для анализа графиков и **Tavily Search API** для сбора "горячих" новостей и инсайдов.

---

## 🚀 Основные возможности

### 1. 📊 Режим "Трейдинг" (Smart Money Concept)
Технический анализ активов с использованием компьютерного зрения.

* **Вход:** Тикер актива + 3 скриншота (Таймфреймы: 1D, 4H, 15m).
* **Анализ:**
    * Поиск SMC паттернов: *Order Blocks, FVG (Fair Value Gaps), BOS (Break of Structure)*.
    * Анализ новостного фона и сентимента за последние 24 часа.
* **Риск-менеджмент:**
    * Автоматический расчет RRR (Risk/Reward Ratio).
    * ⛔ **Фильтр:** Сделки с RRR < 1:2 автоматически отклоняются.
* **Результат:** Готовый торговый сетап (Entry, Stop-Loss, Take-Profit) с аргументацией.

### 2. 💼 Режим "Аналитика" (Value Investing)
Фундаментальный анализ компаний для долгосрочного инвестирования.

* **Вход:** Название компании или тикер.
* **Анализ:**
    * Deep Web Search: поиск отчетов 10-K/10-Q, новостей о конкурентах, судебных исках и инсайдерских продажах.
    * Оценка "Экономического рва" (Moat) и устойчивости бизнес-модели.
* **Результат:**
    * Статус: **Undervalued** (Недооценен) / **Overvalued** (Переоценен).
    * Стратегические цели для покупки/продажи.

### 🆕 Новые функции и обновления
* **Модульная архитектура:** Переход на роутеры (Routers) для лучшей производительности.
* **Улучшенные промпты:** Более точное распознавание графиков.
* *(Добавьте сюда свои новые функции, например: Подключение БД, Админ-панель и т.д.)*

---

## 🛠 Технический стек

* **Язык:** Python 3.10+
* **Фреймворк:** `aiogram 3.x` (Полностью асинхронный)
* **AI Core:** OpenAI GPT-4o (Vision + Text Capabilities)
* **Search Engine:** Tavily API (Optimized for LLMs)
* **Environment:** `python-dotenv` для безопасности

---

## 📂 Структура проекта

Проект обновлен для поддержки масштабируемости:

```text
smart_money_bot/
├── .env                 # API ключи и секреты (не коммитить!)
├── .gitignore           # Исключения для Git
├── requirements.txt     # Зависимости проекта
├── main.py              # Точка входа (Entry point)
├── config.py            # Конфигурация и загрузка переменных
├── services.py          # Логика взаимодействия с AI и Tavily
├── handlers/            # [NEW] Обработчики команд и сообщений
│   ├── __init__.py
│   ├── user_commands.py # Команды /start, /help
│   └── analysis.py      # Логика приема фото и тикеров
├── keyboards/           # [NEW] Клавиатуры и кнопки
│   └── builders.py
└── utils/               # [NEW] Вспомогательные утилиты
⚙️ Установка и запуск
Предварительные требования
Python 3.10 или выше.

API Ключи:

Telegram Bot Token (@BotFather)

OpenAI API Key (platform.openai.com)

Tavily API Key (tavily.com)

Пошаговая инструкция
1. Клонирование репозитория
Bash

git clone [https://github.com/yourusername/smart-money-bot.git](https://github.com/yourusername/smart-money-bot.git)
cd smart-money-bot
2. Виртуальное окружение
Bash

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
3. Установка зависимостей
Bash

pip install -r requirements.txt
4. Настройка .env
Создайте файл .env в корне проекта и добавьте свои ключи:

Ini, TOML

BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
OPENAI_API_KEY=sk-proj-...
TAVILY_API_KEY=tvly-...
5. Запуск
Bash

python main.py
⚠️ Дисклеймер (Disclaimer)
Важно: Этот бот является инструментом для образовательных целей и помощи в анализе.

Не является финансовой рекомендацией. Все решения вы принимаете на свой страх и риск.

Галлюцинации AI. Языковые модели могут ошибаться в расчетах или фактах. Всегда проверяйте уровни и данные перед открытием реальных позиций.

Разработчик не несет ответственности за любые финансовые потери.