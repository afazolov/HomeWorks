"""
Продвинутый Python — Итоговый проект
-------------------------------------
Модуль: models.py
Назначение: SQLAlchemy ORM-модели, приведённые к 3NF.

Схема (3NF):
    brands     — справочник брендов (PK: id, UNIQUE: name)
    categories — справочник категорий (PK: id, UNIQUE: name)
    products   — товары / SKU (PK: id, FK: brand_id → brands, category_id → categories)
    reviews    — отзывы к товарам (PK: id, FK: product_id → products)

Каждая таблица содержит только атрибуты, зависящие исключительно
от её первичного ключа — требование 3NF выполнено.
"""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


# ===========================================================================
# Справочник брендов
# ===========================================================================


class Brand(Base):
    """Бренд товара.

    Атрибуты:
        id   — суррогатный первичный ключ.
        name — уникальное название бренда (напр. «Apple», «Samsung»).
    """

    __tablename__ = "brands"

    id:   Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Обратная связь: список товаров данного бренда
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="brand", lazy="select"
    )

    def __repr__(self) -> str:
        return f"Brand(id={self.id}, name={self.name!r})"


# ===========================================================================
# Справочник категорий
# ===========================================================================


class Category(Base):
    """Категория товара.

    Атрибуты:
        id   — суррогатный первичный ключ.
        name — уникальное название категории (напр. «smartphones», «beauty»).
    """

    __tablename__ = "categories"

    id:   Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Обратная связь: список товаров данной категории
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category", lazy="select"
    )

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name!r})"


# ===========================================================================
# Товар (SKU)
# ===========================================================================


class Product(Base):
    """Товарная единица (SKU).

    Атрибуты:
        id          — первичный ключ (берётся из DummyJSON).
        title       — название товара.
        description — описание.
        price       — цена.
        stock       — остаток на складе.
        rating      — средний рейтинг.
        thumbnail   — URL превью-изображения.
        brand_id    — внешний ключ → brands.id.
        category_id — внешний ключ → categories.id.
    """

    __tablename__ = "products"

    id:          Mapped[int]   = mapped_column(Integer, primary_key=True)
    title:       Mapped[str]   = mapped_column(String(512), nullable=False)
    description: Mapped[str]   = mapped_column(Text, nullable=True)
    price:       Mapped[float] = mapped_column(Float, nullable=False)
    stock:       Mapped[int]   = mapped_column(Integer, nullable=False, default=0)
    rating:      Mapped[float] = mapped_column(Float, nullable=True)
    thumbnail:   Mapped[str]   = mapped_column(Text, nullable=True)

    brand_id:    Mapped[int]   = mapped_column(
        Integer, ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category_id: Mapped[int]   = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Связи к справочникам
    brand:    Mapped["Brand"]    = relationship("Brand",    back_populates="products")
    category: Mapped["Category"] = relationship("Category", back_populates="products")

    # Связь к отзывам
    reviews: Mapped[list["Review"]] = relationship(
        "Review", back_populates="product", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"Product(id={self.id}, title={self.title!r})"


# ===========================================================================
# Отзыв к товару
# ===========================================================================


class Review(Base):
    """Отзыв покупателя на товар.

    Атрибуты:
        id            — суррогатный первичный ключ.
        product_id    — внешний ключ → products.id.
        rating        — оценка (1–5).
        comment       — текст отзыва.
        reviewer_name — имя рецензента.
        reviewer_email— email рецензента.
    """

    __tablename__ = "reviews"

    id:             Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id:     Mapped[int]   = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating:         Mapped[float] = mapped_column(Float, nullable=True)
    comment:        Mapped[str]   = mapped_column(Text, nullable=True)
    reviewer_name:  Mapped[str]   = mapped_column(String(255), nullable=True)
    reviewer_email: Mapped[str]   = mapped_column(String(255), nullable=True)

    # Связь к товару
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")

    def __repr__(self) -> str:
        return f"Review(id={self.id}, product_id={self.product_id}, rating={self.rating})"
