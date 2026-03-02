"""
Продвинутый Python — ДЗ #2
--------------------------
Цель: расширить Loader из ДЗ #1 асинхронным получением данных,
многопоточной загрузкой по категориям и пакетной обработкой.

Запуск: python main.py
"""

from __future__ import annotations

import asyncio
import math
import threading
from abc import ABC, abstractmethod
from typing import Any, Iterable

try:
    import aiohttp
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Не найден пакет 'aiohttp'. Установите его командой: pip install aiohttp"
    ) from exc

try:
    import requests
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Не найден пакет 'requests'. Установите его командой: pip install requests"
    ) from exc


# ===========================================================================
# Базовая модель (абстрактный класс) — взята из ДЗ #1 без изменений
# ===========================================================================


class Model(ABC):
    """Базовый класс модели данных.

    Должен уметь:
    1) Загружать данные по списку категорий.
    2) Преобразовывать данные в словарь.
    """

    url = "https://dummyjson.com/products"

    @abstractmethod
    def download(self, categories: Iterable[str]) -> dict[str, Any]:
        """Получение информации с веб-сайта по массиву категорий."""

    @abstractmethod
    def to_dict(self, data: Any) -> dict[Any, Any]:
        """Преобразование данных с сайта в словарь."""


# ===========================================================================
# Асинхронный загрузчик (Singleton) — расширение Loader из ДЗ #1
# ===========================================================================


class AsyncLoader(Model):
    """Асинхронный загрузчик данных DummyJSON (наследник Model).

    Реализован как Singleton: при создании нескольких экземпляров AsyncLoader
    будет возвращаться один и тот же объект.

    Ключевые возможности (относительно ДЗ #1):
    - ``download``           — синхронная обёртка (обратная совместимость с ДЗ #1).
    - ``download_async``     — асинхронный метод (К1): параллельная загрузка
                               всех категорий через aiohttp.
    - ``_fetch_batch``       — загрузка одного пакета категорий (К3): внутри
                               пакета запросы выполняются параллельно, пакеты —
                               последовательно, что защищает сервер от перегрузки.
    - ``batch_size``         — размер пакета (по умолчанию 5 категорий).
    """

    url = "https://dummyjson.com/products"

    _instance: "AsyncLoader | None" = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "AsyncLoader":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False  # type: ignore[attr-defined]
        return cls._instance

    def __init__(self, timeout: float = 15.0, batch_size: int = 5) -> None:
        if getattr(self, "_initialized", False):
            return

        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._sync_timeout = timeout
        self._batch_size = batch_size
        self._cache: dict[str, dict[int, dict[str, Any]]] = {}
        self._cache_lock = asyncio.Lock()

        self._initialized = True

    # -----------------------------------------------------------------------
    # Публичное свойство
    # -----------------------------------------------------------------------

    @property
    def batch_size(self) -> int:
        return self._batch_size

    # -----------------------------------------------------------------------
    # Реализация абстрактных методов
    # -----------------------------------------------------------------------

    def download(self, categories: Iterable[str]) -> dict[str, Any]:
        """Синхронная обёртка над ``download_async``.

        Сохраняет обратную совместимость с интерфейсом ДЗ #1: можно вызывать
        без создания собственного event-loop.
        """
        return asyncio.run(self.download_async(categories))

    def to_dict(self, data: Any) -> dict[Any, Any]:
        """Преобразует список продуктов DummyJSON в словарь {id: product}.

        Поддерживаемые варианты входных данных:
        - ``dict``       -> возвращается как есть
        - ``list[dict]`` (товары) -> {product_id(int): product_dict}
        - ``None``       -> {}
        """
        if data is None:
            return {}

        if isinstance(data, dict):
            return data

        if not isinstance(data, list):
            raise TypeError(
                "Ожидались данные типа dict | list[dict], получено: "
                f"{type(data)}"
            )

        products_by_id: dict[int, dict[str, Any]] = {}
        for product in data:
            if not isinstance(product, dict):
                continue
            product_id = product.get("id")
            if product_id is None:
                continue
            try:
                product_id_int = int(product_id)
            except (TypeError, ValueError):
                continue
            products_by_id[product_id_int] = product

        return products_by_id

    # -----------------------------------------------------------------------
    # Асинхронные методы (К1, К2, К3)
    # -----------------------------------------------------------------------

    async def download_async(self, categories: Iterable[str]) -> dict[str, Any]:
        """Асинхронная загрузка товаров по категориям с пакетной обработкой (К1, К3).

        Алгоритм:
        1. Дедупликация и очистка входного списка.
        2. Разделение на пакеты по ``batch_size`` категорий (К3).
        3. Каждый пакет загружается параллельно (asyncio.gather) (К2).
        4. Пакеты выполняются последовательно — защита от лавины запросов.

        Возвращает словарь вида:
            {
              "smartphones": {1: {...}, 2: {...}, ...},
              "beauty":      {11: {...}, ...},
            }
        """
        unique_categories = self._deduplicate(categories)
        if not unique_categories:
            raise ValueError("Список категорий пуст. Передайте хотя бы одну категорию.")

        # Разделяем категории на пакеты (К3)
        batches = self._split_into_batches(unique_categories, self._batch_size)

        result: dict[str, Any] = {}

        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            for batch in batches:
                # Внутри пакета — параллельная загрузка (К2)
                batch_result = await self._fetch_batch(session, batch)
                result.update(batch_result)

        return result

    async def _fetch_batch(
        self,
        session: aiohttp.ClientSession,
        categories: list[str],
    ) -> dict[str, Any]:
        """Параллельная загрузка одного пакета категорий (К2).

        Все категории в пакете запрашиваются одновременно через asyncio.gather.
        Результаты берутся из кэша, если уже загружались ранее.
        """
        # Выявляем, что нужно реально скачать (не в кэше)
        to_fetch: list[str] = []
        batch_result: dict[str, Any] = {}

        async with self._cache_lock:
            for category in categories:
                if category in self._cache:
                    batch_result[category] = self._cache[category]
                else:
                    to_fetch.append(category)

        if not to_fetch:
            return batch_result

        # Параллельно скачиваем все отсутствующие в кэше категории
        tasks = [self._fetch_category(session, cat) for cat in to_fetch]
        fetched: list[dict[str, Any]] = await asyncio.gather(*tasks)

        async with self._cache_lock:
            for category, raw in zip(to_fetch, fetched):
                products = raw.get("products", [])
                data_dict = self.to_dict(products)
                self._cache[category] = data_dict
                batch_result[category] = data_dict

        return batch_result

    async def _fetch_category(
        self,
        session: aiohttp.ClientSession,
        category: str,
    ) -> dict[str, Any]:
        """Скачать данные по одной категории асинхронно."""
        url = f"{self.url}/category/{category}"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json(content_type=None)
        except aiohttp.ClientError as exc:
            raise RuntimeError(
                f"Не удалось загрузить категорию '{category}' ({url})"
            ) from exc

    # -----------------------------------------------------------------------
    # Вспомогательные методы
    # -----------------------------------------------------------------------

    @staticmethod
    def _deduplicate(categories: Iterable[str]) -> list[str]:
        """Убрать дубликаты, сохранив порядок."""
        seen: set[str] = set()
        result: list[str] = []
        for category in categories:
            clean = str(category).strip()
            if clean and clean not in seen:
                seen.add(clean)
                result.append(clean)
        return result

    @staticmethod
    def _split_into_batches(items: list[str], batch_size: int) -> list[list[str]]:
        """Разделить список на пакеты заданного размера (К3).

        Аналог np.array_split, но без зависимости от numpy.
        Пример: ['a','b','c','d','e'], batch_size=2 -> [['a','b'],['c','d'],['e']]
        """
        if batch_size <= 0:
            raise ValueError(f"batch_size должен быть > 0, получено: {batch_size}")
        total = len(items)
        n_batches = math.ceil(total / batch_size)
        return [items[i * batch_size : (i + 1) * batch_size] for i in range(n_batches)]


# ===========================================================================
# Быстрая демонстрация работы
# ===========================================================================


if __name__ == "__main__":
    import time

    CATEGORIES = [
        "beauty",
        "fragrances",
        "furniture",
        "groceries",
        "home-decoration",
        "kitchen-accessories",
        "laptops",
        "mens-shirts",
        "mens-shoes",
        "mens-watches",
        "mobile-accessories",
        "motorcycle",
        "skin-care",
        "smartphones",
        "sports-accessories",
        "sunglasses",
        "tablets",
        "tops",
        "vehicle",
        "womens-bags",
        "womens-dresses",
        "womens-jewellery",
        "womens-shoes",
        "womens-watches",
    ]

    loader1 = AsyncLoader(batch_size=5)
    loader2 = AsyncLoader()

    print("Singleton:", loader1 is loader2)
    print(f"Категорий: {len(CATEGORIES)}, размер пакета: {loader1.batch_size}\n")

    start = time.perf_counter()
    data = loader1.download(CATEGORIES)
    elapsed = time.perf_counter() - start

    total_products = sum(len(products) for products in data.values())
    print(f"Загружено категорий : {len(data)}")
    print(f"Товаров всего       : {total_products}")
    print(f"Время загрузки      : {elapsed:.2f} с\n")

    for category, products in list(data.items())[:5]:
        print(f"  {category}: {len(products)} товаров")
    if len(data) > 5:
        print(f"  ... и ещё {len(data) - 5} категорий")
