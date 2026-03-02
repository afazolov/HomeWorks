"""
Продвинутый Python — Итоговый проект
-------------------------------------
Роутер: products.py
Эндпоинты:
    GET /products/                    — все SKU в базе (К5)
    GET /category/{category_name}     — товары указанной категории (К4)
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Category, Product
from schemas import ProductSchema


router = APIRouter(tags=["Products"])

# ===========================================================================
# Простой in-memory кэш с TTL
# ===========================================================================

_cache: dict[str, tuple[float, Any]] = {}
_TTL = 300.0  # секунд


def _cache_get(key: str) -> Any | None:
    """Вернуть значение из кэша если не истёк TTL, иначе None."""
    entry = _cache.get(key)
    if entry is None:
        return None
    ts, value = entry
    if time.monotonic() - ts > _TTL:
        del _cache[key]
        return None
    return value


def _cache_set(key: str, value: Any) -> None:
    """Сохранить значение в кэш с текущей меткой времени."""
    _cache[key] = (time.monotonic(), value)


# ===========================================================================
# Эндпоинты
# ===========================================================================


@router.get("/products/", response_model=list[ProductSchema])
async def get_products(db: Session = Depends(get_db)) -> list[ProductSchema]:
    """Вернуть все SKU, которые есть в базе (К5).

    Результат кэшируется на 5 минут.
    """
    cached = _cache_get("all_products")
    if cached is not None:
        return cached

    products = (
        db.query(Product)
        .options(
            joinedload(Product.brand),
            joinedload(Product.category),
            joinedload(Product.reviews),
        )
        .order_by(Product.id)
        .all()
    )

    result = [ProductSchema.model_validate(p) for p in products]
    _cache_set("all_products", result)
    return result


@router.get("/category/{category_name}", response_model=list[ProductSchema])
async def get_by_category(
    category_name: str,
    db: Session = Depends(get_db),
) -> list[ProductSchema]:
    """Вернуть все товары указанной категории (К4).

    Результат кэшируется на 5 минут.
    """
    cache_key = f"category:{category_name}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    category = (
        db.query(Category)
        .filter(func.lower(Category.name) == category_name.lower())
        .first()
    )
    if category is None:
        raise HTTPException(
            status_code=404,
            detail=f"Категория '{category_name}' не найдена.",
        )

    products = (
        db.query(Product)
        .options(
            joinedload(Product.brand),
            joinedload(Product.category),
            joinedload(Product.reviews),
        )
        .filter(Product.category_id == category.id)
        .order_by(Product.id)
        .all()
    )

    result = [ProductSchema.model_validate(p) for p in products]
    _cache_set(cache_key, result)
    return result
