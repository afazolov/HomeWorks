"""
Продвинутый Python — Итоговый проект
-------------------------------------
Модуль: main.py
Назначение: FastAPI-приложение — точка входа, регистрация роутеров,
            эндпоинт обновления данных и запуск сервера.

Запуск сервера (из папки final/):
    python -m uvicorn main:app --reload

Обновление данных (загрузка с DummyJSON в БД):
    python main.py                              # запускает загрузку и поднимает сервер
    curl -X POST http://localhost:8000/update   # обновить через API

Настройки БД берутся из файла .env (в той же папке):
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from loader import DummyJSONLoader
from routers.brands import router as brands_router
from routers.products import router as products_router
from routers.statistics import router as statistics_router


# ===========================================================================
# Жизненный цикл приложения (lifespan — современный способ вместо on_event)
# ===========================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создать таблицы (если не существуют) при старте приложения."""
    Base.metadata.create_all(bind=engine)
    yield


# ===========================================================================
# Инициализация приложения
# ===========================================================================

app = FastAPI(
    title="DummyJSON Product Catalog API",
    description=(
        "API для работы с каталогом товаров DummyJSON. "
        "Данные хранятся в PostgreSQL, загрузка — асинхронная."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Регистрация роутеров
# ---------------------------------------------------------------------------

app.include_router(products_router)
app.include_router(brands_router)
app.include_router(statistics_router)


# ===========================================================================
# Служебные эндпоинты
# ===========================================================================


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Корневой эндпоинт — проверка работоспособности сервиса."""
    return {
        "service": "DummyJSON Product Catalog API",
        "status":  "ok",
        "docs":    "/docs",
    }


@app.post("/update", tags=["Data"])
async def update_data(db: Session = Depends(get_db)) -> dict:
    """Скачать все данные с DummyJSON и сохранить/обновить в БД (К1, К2, К3).

    Использует асинхронный DummyJSONLoader с пакетной загрузкой.
    Возвращает количество сохранённых товаров по каждой категории.
    """
    loader = DummyJSONLoader(batch_size=5)
    result = await loader.load(db)
    total  = sum(result.values())
    return {
        "status":      "ok",
        "total_saved": total,
        "by_category": result,
    }


# ===========================================================================
# Точка входа — запуск сервера через python main.py
# ===========================================================================


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,   # reload=True несовместим с прямым запуском через __main__
    )
