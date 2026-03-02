"""
Продвинутый Python — ДЗ #1
--------------------------
Цель: на практике понять наследование, абстрактные методы и паттерн
«Синглтон» на примере загрузки данных с DummyJSON.

Запуск: python main.py
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable
import json
import threading


try:
    import requests
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Не найден пакет 'requests'. Установите его командой: pip install requests"
    ) from exc


# ===========================================================================
# Базовая модель (абстрактный класс)
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
# Наследник для DummyJSON + Singleton
# ===========================================================================


class Loader(Model):
    """Загрузчик данных DummyJSON (наследник Model).

    Реализован как Singleton: при создании нескольких экземпляров Loader
    будет возвращаться один и тот же объект.
    """

    url = "https://dummyjson.com/products"

    _instance: "Loader | None" = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "Loader":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False  # type: ignore[attr-defined]
        return cls._instance

    def __init__(self, timeout: float = 15.0) -> None:
        if getattr(self, "_initialized", False):
            return

        self._timeout = timeout
        self._session = requests.Session()
        self._cache: dict[str, dict[int, dict[str, Any]]] = {}

        self._initialized = True

    # -----------------------------------------------------------------------
    # Реализация абстрактных методов
    # -----------------------------------------------------------------------

    def download(self, categories: Iterable[str]) -> dict[str, Any]:
        """Загружает товары DummyJSON по категориям.

        Возвращает словарь вида:
            {
              "smartphones": {1: {...}, 2: {...}, ...},
              "beauty":      {11: {...}, ...},
            }
        """
        categories_list = [str(c).strip() for c in categories if str(c).strip()]
        if not categories_list:
            raise ValueError("Список категорий пуст. Передайте хотя бы одну категорию.")

        unique_categories: list[str] = []
        seen: set[str] = set()
        for category in categories_list:
            if category not in seen:
                seen.add(category)
                unique_categories.append(category)

        result: dict[str, Any] = {}
        for category in unique_categories:
            if category in self._cache:
                result[category] = self._cache[category]
                continue

            raw = self._download_category(category)
            products = raw.get("products", [])
            data_dict = self.to_dict(products)

            self._cache[category] = data_dict
            result[category] = data_dict

        return result

    def to_dict(self, data: Any) -> dict[Any, Any]:
        """Преобразует данные DummyJSON в словарь.

        Поддерживаемые варианты входных данных:
        - `requests.Response` -> `response.json()` (ожидается dict)
        - `str/bytes` -> JSON -> dict
        - `dict` -> возвращается как есть
        - `list[dict]` (товары) -> {product_id(int): product_dict}
        """
        if data is None:
            return {}

        if isinstance(data, requests.Response):
            payload = data.json()
            if not isinstance(payload, dict):
                raise TypeError("Ожидался JSON-объект (dict) в ответе DummyJSON.")
            return payload

        if isinstance(data, (str, bytes, bytearray)):
            try:
                payload = json.loads(data)
            except json.JSONDecodeError as exc:
                raise ValueError("Строка не является валидным JSON.") from exc
            if not isinstance(payload, dict):
                raise TypeError("Ожидался JSON-объект (dict).")
            return payload

        if isinstance(data, dict):
            return data

        if not isinstance(data, list):
            raise TypeError(
                "Ожидались данные типа requests.Response | dict | str/bytes | list[dict], получено: "
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
    # Внутренние методы
    # -----------------------------------------------------------------------

    def _download_category(self, category: str) -> dict[str, Any]:
        """Скачать данные по одной категории."""
        url = f"{self.url}/category/{category}"
        try:
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Не удалось загрузить категорию '{category}' ({url})") from exc

        data = self.to_dict(response)
        if not isinstance(data, dict):  # защита на случай изменения логики to_dict
            raise RuntimeError("DummyJSON вернул неожиданный формат данных.")
        return data


# ===========================================================================
# Быстрая демонстрация работы
# ===========================================================================


if __name__ == "__main__":
    loader1 = Loader()
    loader2 = Loader()

    print("Singleton:", loader1 is loader2)

    data = loader1.download(["beauty", "smartphones"])
    for category, products in data.items():
        print(f"{category}: {len(products)} товаров")
