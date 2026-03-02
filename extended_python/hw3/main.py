"""
Продвинутый Python — ДЗ #3
--------------------------
Цель: расширить AsyncLoader из ДЗ #2 многопоточной загрузкой данных
с использованием ThreadPoolExecutor и методом map.

Запуск: python main.py
"""

from __future__ import annotations

import math
import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Iterable

try:
    import requests
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Не найден пакет 'requests'. Установите его командой: pip install requests"
    ) from exc

try:
    import numpy as np  # type: ignore[import]
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


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
# Многопоточный загрузчик (Singleton) — расширение AsyncLoader из ДЗ #2
# ===========================================================================


class ThreadedLoader(Model):
    """Многопоточный загрузчик данных DummyJSON (наследник Model).

    Реализован как Singleton: при создании нескольких экземпляров ThreadedLoader
    будет возвращаться один и тот же объект.

    Ключевые возможности (относительно ДЗ #2):
    - ``download``           — основной метод загрузки: разбивает категории на
                               пакеты и запускает многопоточную загрузку (К1, К2, К3).
    - ``_download_batch``    — загружает один пакет категорий через
                               ThreadPoolExecutor.map (К1, К2).
    - ``_split_into_batches``— разбивает список категорий на пакеты (К3):
                               использует np.array_split если numpy доступен,
                               иначе стандартное разделение списка.
    - ``max_workers``        — максимальное количество потоков в пуле.
    - ``batch_size``         — размер пакета категорий.
    """

    url = "https://dummyjson.com/products"

    _instance: "ThreadedLoader | None" = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "ThreadedLoader":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False  # type: ignore[attr-defined]
        return cls._instance

    def __init__(
        self,
        timeout: float = 15.0,
        batch_size: int = 5,
        max_workers: int = 8,
    ) -> None:
        if getattr(self, "_initialized", False):
            return

        self._timeout = timeout
        self._batch_size = batch_size
        self._max_workers = max_workers
        self._session = requests.Session()
        self._cache: dict[str, dict[int, dict[str, Any]]] = {}
        self._cache_lock = threading.Lock()

        self._initialized = True

    # -----------------------------------------------------------------------
    # Публичные свойства
    # -----------------------------------------------------------------------

    @property
    def batch_size(self) -> int:
        return self._batch_size

    @property
    def max_workers(self) -> int:
        return self._max_workers

    # -----------------------------------------------------------------------
    # Реализация абстрактных методов
    # -----------------------------------------------------------------------

    def download(self, categories: Iterable[str]) -> dict[str, Any]:
        """Многопоточная загрузка товаров по категориям с пакетной обработкой.

        Алгоритм:
        1. Дедупликация и очистка входного списка.
        2. Разделение на пакеты по ``batch_size`` категорий (К3).
        3. Каждый пакет обрабатывается через ThreadPoolExecutor.map (К1, К2).
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
        for batch in batches:
            batch_result = self._download_batch(batch)
            result.update(batch_result)

        return result

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
    # Многопоточные методы (К1, К2)
    # -----------------------------------------------------------------------

    def _download_batch(self, categories: list[str]) -> dict[str, Any]:
        """Многопоточная загрузка одного пакета категорий (К1, К2).

        Использует ThreadPoolExecutor.map: каждой категории из пакета
        соответствует один поток, вызывающий ``_fetch_category``.
        Результаты собираются в том же порядке, что и входной список.
        """
        # Выявляем категории, которых нет в кэше
        to_fetch: list[str] = []
        batch_result: dict[str, Any] = {}

        with self._cache_lock:
            for category in categories:
                if category in self._cache:
                    batch_result[category] = self._cache[category]
                else:
                    to_fetch.append(category)

        if not to_fetch:
            return batch_result

        # Многопоточная загрузка через ThreadPoolExecutor.map (К1)
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            fetched = list(executor.map(self._fetch_category, to_fetch))

        with self._cache_lock:
            for category, raw in zip(to_fetch, fetched):
                products = raw.get("products", [])
                data_dict = self.to_dict(products)
                self._cache[category] = data_dict
                batch_result[category] = data_dict

        return batch_result

    def _fetch_category(self, category: str) -> dict[str, Any]:
        """Скачать данные по одной категории (выполняется в отдельном потоке)."""
        url = f"{self.url}/category/{category}"
        try:
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
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
        """Разделить список категорий на пакеты заданного размера (К3).

        Использует np.array_split если numpy установлен, иначе — стандартное
        разделение списка через срезы.

        Пример: ['a','b','c','d','e'], batch_size=2 -> [['a','b'],['c','d'],['e']]
        """
        if batch_size <= 0:
            raise ValueError(f"batch_size должен быть > 0, получено: {batch_size}")

        if _HAS_NUMPY:
            n_batches = math.ceil(len(items) / batch_size)
            return [arr.tolist() for arr in np.array_split(items, n_batches)]

        n_batches = math.ceil(len(items) / batch_size)
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

    loader1 = ThreadedLoader(batch_size=5, max_workers=8)
    loader2 = ThreadedLoader()

    print("Singleton      :", loader1 is loader2)
    print(f"Категорий      : {len(CATEGORIES)}")
    print(f"Размер пакета  : {loader1.batch_size}")
    print(f"Потоков в пуле : {loader1.max_workers}")
    print(f"numpy доступен : {_HAS_NUMPY}\n")

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
