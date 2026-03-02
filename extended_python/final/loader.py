"""
Продвинутый Python — Итоговый проект
-------------------------------------
Модуль: loader.py
Назначение: асинхронная загрузка данных с DummyJSON (на основе AsyncLoader
            из ДЗ #2) и асинхронное сохранение в базу данных.

Алгоритм:
    1. Получить список всех категорий DummyJSON (/products/categories).
    2. Разбить категории на пакеты (batch_size).
    3. Параллельно (asyncio.gather) скачать товары каждого пакета (К2).
    4. Разобрать каждый товар на сущности: Brand, Category, Product, Review.
    5. Асинхронно (через run_in_executor) сохранить всё в PostgreSQL (К3).
"""

from __future__ import annotations

import asyncio
import math
import threading
from typing import Any

try:
    import aiohttp
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Не найден пакет 'aiohttp'. Установите его командой: pip install aiohttp"
    ) from exc

from sqlalchemy.orm import Session

from models import Brand, Category, Product, Review


# ===========================================================================
# Вспомогательные утилиты
# ===========================================================================


def _split_into_batches(items: list[str], batch_size: int) -> list[list[str]]:
    """Разделить список на пакеты заданного размера.

    Пример: ['a','b','c','d','e'], batch_size=2 -> [['a','b'],['c','d'],['e']]
    """
    if batch_size <= 0:
        raise ValueError(f"batch_size должен быть > 0, получено: {batch_size}")
    n_batches = math.ceil(len(items) / batch_size)
    return [items[i * batch_size : (i + 1) * batch_size] for i in range(n_batches)]


def _get_or_create_brand(db: Session, name: str) -> Brand:
    """Получить бренд из БД или создать новый (upsert по name)."""
    brand = db.query(Brand).filter(Brand.name == name).first()
    if brand is None:
        brand = Brand(name=name)
        db.add(brand)
        db.flush()  # получаем brand.id до commit
    return brand


def _get_or_create_category(db: Session, name: str) -> Category:
    """Получить категорию из БД или создать новую (upsert по name)."""
    category = db.query(Category).filter(Category.name == name).first()
    if category is None:
        category = Category(name=name)
        db.add(category)
        db.flush()
    return category


def _save_products(db: Session, raw_products: list[dict[str, Any]]) -> int:
    """Сохранить список сырых товаров DummyJSON в БД.

    Разбирает каждый товар на Brand, Category, Product, Review.
    Возвращает количество сохранённых товаров.
    """
    saved = 0
    for raw in raw_products:
        product_id = raw.get("id")
        if product_id is None:
            continue

        # --- Бренд ---
        brand_name = (raw.get("brand") or "").strip() or "Unknown"
        brand = _get_or_create_brand(db, brand_name)

        # --- Категория ---
        category_name = (raw.get("category") or "").strip() or "Unknown"
        category = _get_or_create_category(db, category_name)

        # --- Товар (upsert по id из DummyJSON) ---
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            product = Product(id=product_id)
            db.add(product)

        product.title       = raw.get("title", "")
        product.description = raw.get("description")
        product.price       = float(raw.get("price", 0))
        product.stock       = int(raw.get("stock", 0))
        product.rating      = raw.get("rating")
        product.thumbnail   = raw.get("thumbnail")
        product.brand_id    = brand.id
        product.category_id = category.id

        db.flush()

        # --- Отзывы (пересохраняем при каждом обновлении) ---
        db.query(Review).filter(Review.product_id == product_id).delete()
        for raw_review in raw.get("reviews", []):
            review = Review(
                product_id     = product_id,
                rating         = raw_review.get("rating"),
                comment        = raw_review.get("comment"),
                reviewer_name  = raw_review.get("reviewerName"),
                reviewer_email = raw_review.get("reviewerEmail"),
            )
            db.add(review)

        saved += 1

    db.commit()
    return saved


# ===========================================================================
# DummyJSONLoader — асинхронная загрузка + сохранение в БД
# ===========================================================================


class DummyJSONLoader:
    """Асинхронный загрузчик данных DummyJSON с сохранением в PostgreSQL.

    Реализован как Singleton: все экземпляры — один объект.

    Ключевые методы:
    - ``fetch_all_categories``  — получить список всех категорий DummyJSON.
    - ``load``                  — основной метод: скачать всё и сохранить в БД.
    - ``_fetch_category``       — скачать товары одной категории асинхронно.
    - ``_fetch_batch``          — параллельная загрузка пакета категорий (К2).
    """

    BASE_URL = "https://dummyjson.com/products"

    _instance: "DummyJSONLoader | None" = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "DummyJSONLoader":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False  # type: ignore[attr-defined]
        return cls._instance

    def __init__(self, timeout: float = 30.0, batch_size: int = 5) -> None:
        if getattr(self, "_initialized", False):
            return

        self._timeout    = aiohttp.ClientTimeout(total=timeout)
        self._batch_size = batch_size
        self._initialized = True

    # -----------------------------------------------------------------------
    # Публичное свойство
    # -----------------------------------------------------------------------

    @property
    def batch_size(self) -> int:
        return self._batch_size

    # -----------------------------------------------------------------------
    # Основной метод загрузки (К1, К2, К3)
    # -----------------------------------------------------------------------

    async def load(self, db: Session) -> dict[str, int]:
        """Скачать все товары с DummyJSON и асинхронно сохранить в БД (К3).

        Алгоритм:
        1. Получить список категорий.
        2. Разбить на пакеты (batch_size).
        3. Каждый пакет загрузить параллельно (asyncio.gather) (К2).
        4. Сохранить результаты в БД через run_in_executor (К3).

        Возвращает словарь {category: кол-во сохранённых товаров}.
        """
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            categories = await self.fetch_all_categories(session)
            batches    = _split_into_batches(categories, self._batch_size)

            result: dict[str, int] = {}
            loop = asyncio.get_event_loop()

            for batch in batches:
                # Параллельная загрузка пакета (К2)
                raw_by_category = await self._fetch_batch(session, batch)

                for category_name, raw_products in raw_by_category.items():
                    # Асинхронное сохранение в БД через пул потоков (К3)
                    saved = await loop.run_in_executor(
                        None, _save_products, db, raw_products
                    )
                    result[category_name] = saved

        return result

    # -----------------------------------------------------------------------
    # Асинхронные вспомогательные методы (К2)
    # -----------------------------------------------------------------------

    async def fetch_all_categories(
        self, session: aiohttp.ClientSession
    ) -> list[str]:
        """Получить список всех доступных категорий DummyJSON."""
        url = f"{self.BASE_URL}/category-list"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
                return [str(c) for c in data if c]
        except aiohttp.ClientError as exc:
            raise RuntimeError(
                f"Не удалось получить список категорий ({url})"
            ) from exc

    async def _fetch_batch(
        self,
        session: aiohttp.ClientSession,
        categories: list[str],
    ) -> dict[str, list[dict[str, Any]]]:
        """Параллельная загрузка пакета категорий (К2).

        Все категории в пакете запрашиваются одновременно через asyncio.gather.
        Возвращает {category_name: [product_dict, ...]}.
        """
        tasks = [self._fetch_category(session, cat) for cat in categories]
        results: list[list[dict[str, Any]]] = await asyncio.gather(*tasks)
        return dict(zip(categories, results))

    async def _fetch_category(
        self,
        session: aiohttp.ClientSession,
        category: str,
    ) -> list[dict[str, Any]]:
        """Скачать товары одной категории асинхронно."""
        url = f"{self.BASE_URL}/category/{category}"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
                return data.get("products", [])
        except aiohttp.ClientError as exc:
            raise RuntimeError(
                f"Не удалось загрузить категорию '{category}' ({url})"
            ) from exc
