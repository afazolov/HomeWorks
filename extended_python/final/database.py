"""
Продвинутый Python — Итоговый проект
-------------------------------------
Модуль: database.py
Назначение: настройка подключения к PostgreSQL через SQLAlchemy,
            фабрика сессий и зависимость FastAPI get_db.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Загружаем .env из папки этого файла
load_dotenv(Path(__file__).parent / ".env")

# ===========================================================================
# Конфигурация подключения
# ===========================================================================

# Параметры берутся из .env / переменных окружения.
_DB_USER     = os.getenv("DB_USER",     "postgres")
_DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
_DB_HOST     = os.getenv("DB_HOST",     "localhost")
_DB_PORT     = os.getenv("DB_PORT",     "5432")
_DB_NAME     = os.getenv("DB_NAME",     "synergy")

DATABASE_URL = (
    f"postgresql+psycopg2://{_DB_USER}:{_DB_PASSWORD}"
    f"@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}"
)

# ===========================================================================
# Engine и фабрика сессий
# ===========================================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # проверять соединение перед использованием
    pool_size=10,
    max_overflow=20,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ===========================================================================
# Базовый класс ORM-моделей
# ===========================================================================


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy-моделей проекта."""


# ===========================================================================
# Зависимость FastAPI
# ===========================================================================


def get_db():
    """Генератор сессии БД — используется как Depends(get_db) в роутерах."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
