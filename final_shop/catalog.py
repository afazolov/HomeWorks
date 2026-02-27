"""
Каталог товаров: хранение, добавление, редактирование, удаление.
"""
from models import Product


class Catalog:
    """Управляет списком товаров магазина."""

    def __init__(self):
        self._products: list[Product] = []
        self._next_id: int = 1

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add(self, name: str, category: str, price: float,
            weight: float, description: str = "") -> Product:
        """Добавить новый товар. Возвращает созданный Product."""
        if price < 0 or weight < 0:
            raise ValueError("Цена и вес не могут быть отрицательными")
        p = Product(
            id=self._next_id,
            name=name.strip(),
            category=category.strip(),
            price=price,
            weight=weight,
            description=description.strip(),
        )
        self._products.append(p)
        self._next_id += 1
        return p

    def get(self, product_id: int) -> Product | None:
        """Найти товар по id. Возвращает None если не найден."""
        for p in self._products:
            if p.id == product_id:
                return p
        return None

    def update(self, product_id: int, **kwargs) -> Product:
        """Изменить поля товара по id. Возвращает обновлённый Product."""
        p = self.get(product_id)
        if p is None:
            raise KeyError(f"Товар с id={product_id} не найден")
        for field, value in kwargs.items():
            if not hasattr(p, field):
                raise AttributeError(f"Неизвестное поле: {field}")
            if field in ("price", "weight") and value < 0:
                raise ValueError(f"Поле '{field}' не может быть отрицательным")
            setattr(p, field, value)
        return p

    def remove(self, product_id: int) -> None:
        """Удалить товар из каталога по id."""
        p = self.get(product_id)
        if p is None:
            raise KeyError(f"Товар с id={product_id} не найден")
        self._products.remove(p)

    def all(self) -> list[Product]:
        """Вернуть все товары каталога."""
        return list(self._products)

    # ------------------------------------------------------------------
    # Предзаполненный каталог
    # ------------------------------------------------------------------

    @classmethod
    def default(cls) -> "Catalog":
        """Создаёт каталог с товарами для демонстрации."""
        c = cls()
        items = [
            # name, category, price, weight, description
            ("Яблоко",          "Фрукты",      35.00,   182, "Сладкое, сорт Гала"),
            ("Банан",           "Фрукты",      89.00,   120, "Спелый, 1 шт."),
            ("Апельсин",        "Фрукты",      59.90,   200, "Сочный, без косточек"),
            ("Молоко 1 л",      "Молочное",    79.00,  1030, "Пастеризованное 3,2%"),
            ("Кефир 0,5 л",     "Молочное",    55.50,   510, "Классический 2,5%"),
            ("Творог 200 г",    "Молочное",    89.90,   200, "Зернистый 9%"),
            ("Хлеб ржаной",     "Выпечка",     42.00,   400, "Нарезной"),
            ("Батон",           "Выпечка",     38.50,   350, "Пшеничный нарезной"),
            ("Круассан",        "Выпечка",     65.00,    90, "С маслом"),
            ("Куриное филе",    "Мясо",       289.00,   500, "Охлаждённое"),
            ("Говядина",        "Мясо",       549.00,   500, "Вырезка"),
            ("Свинина",         "Мясо",       369.00,   500, "Шея"),
            ("Гречка 900 г",    "Крупы",       79.90,   900, "Ядрица"),
            ("Рис 900 г",       "Крупы",       69.00,   900, "Пропаренный"),
            ("Овсянка 500 г",   "Крупы",       55.00,   500, "Быстрого приготовления"),
            ("Кофе молотый",    "Напитки",    349.00,   250, "Арабика 100%"),
            ("Чай чёрный",      "Напитки",    129.00,   100, "Ассам, 25 пакетиков"),
            ("Сок апельсиновый","Напитки",     89.00,   950, "Прямого отжима 1 л"),
            ("Шоколад",         "Сладости",    99.00,   100, "Горький 72%"),
            ("Печенье",         "Сладости",    75.00,   250, "Овсяное"),
        ]
        for name, cat, price, weight, desc in items:
            c.add(name, cat, price, weight, desc)
        return c
