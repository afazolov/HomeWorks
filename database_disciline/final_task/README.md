# To-Do Telegram Bot

Бот для управления списком задач. Работает в двух режимах:
- **PostgreSQL** — данные сохраняются между перезапусками
- **In-memory** — если PostgreSQL недоступен, данные хранятся в памяти

## Быстрый старт

### 1. Установить зависимости

```bash
pip install -r requirements.txt
```

### 2. Создать файл `.env`

Скопировать шаблон и заполнить своими данными:

```bash
cp .env.example .env
```

Открыть `.env` и вставить токен бота (получить у [@BotFather](https://t.me/BotFather)):

```
BOT_TOKEN=1234567890:AAAA...
```

### 3. Создать базу данных PostgreSQL

```sql
CREATE DATABASE todo_bot;
```

> Таблица `tasks` создаётся автоматически при первом запуске бота.

Прописать параметры подключения в `.env`:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todo_bot
DB_USER=postgres
DB_PASSWORD=ваш_пароль
```

### 4. Запустить бота

```bash
python bot.py
```

---

## Команды бота

| Команда | Описание |
|---|---|
| `/start` | Приветственное сообщение |
| `/help` | Список команд |
| `/add <название>` | Добавить задачу |
| `/list` | Показать все задачи |
| `/complete <номер>` | Отметить задачу выполненной |
| `/delete <номер>` | Удалить задачу |

## Структура проекта

```
final_task/
├── bot.py          — обработчики команд Telegram
├── models.py       — класс Task
├── database.py     — работа с PostgreSQL / in-memory fallback
├── requirements.txt
├── .env.example    — шаблон конфига
└── .env            — ваши секреты (не коммитить!)
```
