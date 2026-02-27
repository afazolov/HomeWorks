"""
Корзина покупок: добавление, удаление, изменение кол-ва, подсчёт итога.
"""
from models import Product, CartItem


class Cart:
    """Управляет позициями корзины покупок."""

    DISCOUNT_THRESHOLD = 1000.0   # Скидка при сумме больше порога
    DISCOUNT_RATE      = 0.05     # 5 % скидка
    TAX_RATE           = 0.00     # НДС (0 — включён в цену, можно изменить)

    def __init__(self):
        # Хранение: id товара → CartItem
        self._items: dict[int, CartItem] = {}

    # ------------------------------------------------------------------
    # Операции с позициями
    # ------------------------------------------------------------------

    def add(self, product: Product, qty: int = 1) -> None:
        """Добавить товар в корзину. Если уже есть — увеличить кол-во."""
        if qty <= 0:
            raise ValueError("Количество должно быть больше нуля")
        if product.id in self._items:
            self._items[product.id].qty += qty
        else:
            self._items[product.id] = CartItem(product=product, qty=qty)

    def remove(self, product_id: int) -> None:
        """Полностью удалить позицию из корзины."""
        if product_id not in self._items:
            raise KeyError(f"Товар с id={product_id} не найден в корзине")
        del self._items[product_id]

    def change_qty(self, product_id: int, delta: int) -> None:
        """
        Изменить количество товара на delta.
        Если кол-во становится <= 0 — удалить позицию.
        """
        if product_id not in self._items:
            raise KeyError(f"Товар с id={product_id} не найден в корзине")
        item = self._items[product_id]
        item.qty += delta
        if item.qty <= 0:
            del self._items[product_id]

    def clear(self) -> None:
        """Очистить корзину."""
        self._items.clear()

    # ------------------------------------------------------------------
    # Просмотр
    # ------------------------------------------------------------------

    def items(self) -> list[CartItem]:
        """Вернуть список позиций корзины."""
        return list(self._items.values())

    def set_items(self, items: list[CartItem]) -> None:
        """Заменить содержимое корзины (используется после сортировки)."""
        self._items = {item.product.id: item for item in items}

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def size(self) -> int:
        return len(self._items)

    # ------------------------------------------------------------------
    # Подсчёт стоимости (K4: скидки и налоги)
    # ------------------------------------------------------------------

    def subtotal(self) -> float:
        """Сумма без скидки и налогов."""
        return sum(item.total_price for item in self._items.values())

    def discount(self) -> float:
        """Размер скидки в рублях (5% при сумме > 1000 руб.)."""
        sub = self.subtotal()
        if sub > self.DISCOUNT_THRESHOLD:
            return round(sub * self.DISCOUNT_RATE, 2)
        return 0.0

    def tax(self) -> float:
        """Налог (НДС) в рублях."""
        return round((self.subtotal() - self.discount()) * self.TAX_RATE, 2)

    def total(self) -> float:
        """Итоговая сумма: subtotal − скидка + налог."""
        return round(self.subtotal() - self.discount() + self.tax(), 2)

    def total_weight(self) -> float:
        """Общий вес корзины в граммах."""
        return sum(item.total_weight for item in self._items.values())
