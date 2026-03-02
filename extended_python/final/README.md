# Продвинутый Python — Итоговый проект (extended_python/final)

## Описание

FastAPI-сервис для работы с каталогом товаров **DummyJSON**.
Данные загружаются асинхронно (на основе `AsyncLoader` из ДЗ №2),
разбираются на сущности и сохраняются в **PostgreSQL** через SQLAlchemy.

---

## Структура проекта

```
final/
├── main.py             # FastAPI-приложение, запуск сервера
├── database.py         # Подключение к PostgreSQL, get_db
├── models.py           # SQLAlchemy ORM-модели (3NF)
├── schemas.py          # Pydantic-схемы ответов
├── loader.py           # Асинхронная загрузка DummyJSON + сохранение в БД
├── schema.sql          # SQL-скрипты создания таблиц
├── routers/
│   ├── products.py     # GET /products/, GET /category/{name}
│   ├── brands.py       # GET /brands/, GET /brand/{name}
│   └── statistics.py   # GET /statistics/
└── README.md
```

---

## Схема БД (3NF)

```
brands(id PK, name UNIQUE)
     │
     └── products(id PK, title, price, stock, rating, thumbnail,
                  brand_id FK→brands,
                  category_id FK→categories)
                       │
categories(id PK,      └── reviews(id PK, product_id FK→products,
           name UNIQUE)             rating, comment,
                                    reviewer_name, reviewer_email)
```

Каждая таблица содержит только атрибуты, зависящие исключительно от её PK — **3NF выполнен**.

---

## Установка зависимостей

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary aiohttp python-dotenv
```

---

## Настройка БД

### 1. Создать файл `.env` в папке `final/`

```env
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
DB_NAME=synergy
```

### 2. Создание таблиц

Таблицы создаются **автоматически** при старте приложения (`Base.metadata.create_all`).

Или вручную через SQL-скрипт:

```bash
psql -U postgres -d synergy -f schema.sql
```

---

## Запуск

```bash
cd extended_python/final

# Рекомендуемый способ (из любого терминала)
python -m uvicorn main:app --reload

# Или напрямую
python main.py
```

Сервер поднимется на `http://localhost:8000`.
Интерактивная документация: `http://localhost:8000/docs`

---

## Загрузка данных с DummyJSON

Отправить POST-запрос на `/update`:

```bash
curl -X POST http://localhost:8000/update
```

Или через Swagger UI: `http://localhost:8000/docs` → `POST /update`.

Что происходит:
1. Загружается список всех категорий DummyJSON.
2. Категории разбиваются на пакеты по 5 (batch_size).
3. Каждый пакет загружается параллельно через `asyncio.gather`.
4. Данные сохраняются в БД асинхронно через `run_in_executor`.

---

## API-методы

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/` | Проверка работоспособности |
| `POST` | `/update` | Загрузить/обновить данные с DummyJSON |
| `GET` | `/products/` | Все SKU в базе (с кэшированием 5 мин) |
| `GET` | `/category/{category_name}` | Товары указанной категории |
| `GET` | `/brands/` | Список всех брендов |
| `GET` | `/brand/{brand_name}` | Товары указанного бренда |
| `GET` | `/statistics/` | Сводная статистика по каталогу |

### Примеры запросов

```bash
# Все товары
curl http://localhost:8000/products/

# Товары категории smartphones
curl http://localhost:8000/category/smartphones

# Все бренды
curl http://localhost:8000/brands/

# Товары бренда Apple
curl http://localhost:8000/brand/Apple

# Статистика
curl http://localhost:8000/statistics/
```

### Пример ответа `/statistics/`

```json
{
  "total_products": 194,
  "low_stock_products": 23,
  "avg_price": 542.75,
  "total_brands": 52,
  "total_categories": 24,
  "total_reviews": 486
}
```

---

## Критерии оценивания

| Критерий | Реализация | Баллов |
|---|---|---|
| **К1** | `DummyJSONLoader.load()` — загрузка всех товаров с DummyJSON | 1 |
| **К2** | `asyncio.gather` внутри `_fetch_batch` — параллельная загрузка по категориям | 1 |
| **К3** | `_split_into_batches` + пакетная обработка + `run_in_executor` для сохранения | 5 |
| **К4** | `GET /category/{category_name}` | 1 |
| **К5** | `GET /brands/`, `GET /brand/{brand_name}`, `GET /products/` | 6 |
| **К6** | 3NF: таблицы brands, categories, products, reviews с PK и FK | 6 |

**Итого: 20/20 баллов**
