# 🌤️ Weather App

Простое веб-приложение на **FastAPI** для отображения текущей погоды в выбранном городе. Используется [Open-Meteo API](https://open-meteo.com/) и реализованы функции автодополнения, сохранения истории и статистики запросов.

---

## 🔧 Возможности

- 🔍 Поиск погоды по городу
- ✨ Автодополнение при вводе названия города
- 💾 Запоминание последнего города (в сессии)
- 📊 Подсчёт количества запросов по каждому городу
- ⚡ Мгновенное отображение результата на той же странице

---

## 📦 Зависимости

Указаны в `requirements.txt`:

```text
fastapi
uvicorn
jinja2
httpx
sqlalchemy
pytest
pytest-asyncio
```

Установка:

``pip install -r requirements.txt``

## 🚀 Как запустить

### Клонировать репозиторий:
```text
git clone https://github.com/skr1pmen/weather-fastapi.git
cd weather-fastapi
```

### Установить зависимости:

```pip install -r requirements.txt```

### Запустить приложение:

```
uvicorn main:app --reload
```

Открой в браузере: http://localhost:8000

## 🗂 Структура проекта
```text
weather-app/
│
├── main.py                 # Основной файл FastAPI приложения
├── test_main.py            # Автоматические тесты
├── requirements.txt        # Зависимости проекта
│
├── templates/
│   └── index.html          # Главный HTML-шаблон
│
├── static/
│   └── ...                 # Статические файлы (JS, CSS)
│
└── weather.db              # SQLite база данных (создаётся автоматически)
```
