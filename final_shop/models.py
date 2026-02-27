"""
Модели данных: Product и CartItem
"""
from dataclasses import dataclass, field


@dataclass
class Product:
    """Товар в каталоге."""
    id: int
    name: str
    category: str
    price: float        # рублей
    weight: float       # граммы
    description: str = ""

    def __str__(self) -> str:
        return f"{self.name} ({self.category}) — {self.price:.2f} руб., {self.weight} г"


@dataclass
class CartItem:
    """Позиция в корзине: товар + количество."""
    product: Product
    qty: int = 1

    @property
    def total_price(self) -> float:
        """Сумма позиции = цена × количество."""
        return self.product.price * self.qty

    @property
    def total_weight(self) -> float:
        """Вес позиции = вес × количество."""
        return self.product.weight * self.qty
