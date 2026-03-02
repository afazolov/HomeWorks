"""
Продвинутый Python — Итоговый проект
-------------------------------------
Модуль: schemas.py
Назначение: Pydantic-схемы для сериализации ответов FastAPI.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# ===========================================================================
# Review
# ===========================================================================


class ReviewSchema(BaseModel):
    """Отзыв на товар."""

    model_config = ConfigDict(from_attributes=True)

    id:             int
    rating:         float | None
    comment:        str   | None
    reviewer_name:  str   | None
    reviewer_email: str   | None


# ===========================================================================
# Brand
# ===========================================================================


class BrandSchema(BaseModel):
    """Краткая информация о бренде (для списка брендов)."""

    model_config = ConfigDict(from_attributes=True)

    id:   int
    name: str


# ===========================================================================
# Category
# ===========================================================================


class CategorySchema(BaseModel):
    """Краткая информация о категории."""

    model_config = ConfigDict(from_attributes=True)

    id:   int
    name: str


# ===========================================================================
# Product
# ===========================================================================


class ProductSchema(BaseModel):
    """Полная карточка товара (SKU) с вложенными брендом и категорией."""

    model_config = ConfigDict(from_attributes=True)

    id:          int
    title:       str
    description: str   | None
    price:       float
    stock:       int
    rating:      float | None
    thumbnail:   str   | None
    brand:       BrandSchema    | None
    category:    CategorySchema | None
    reviews:     list[ReviewSchema] = []


# ===========================================================================
# Statistics
# ===========================================================================


class StatisticsSchema(BaseModel):
    """Статистика по каталогу товаров."""

    total_products:    int
    low_stock_products: int
    avg_price:         float | None
    total_brands:      int
    total_categories:  int
    total_reviews:     int
