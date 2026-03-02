"""
Продвинутый Python — Итоговый проект
-------------------------------------
Роутер: brands.py
Эндпоинты:
    GET /brands/                  — список всех брендов (К5)
    GET /brand/{brand_name}       — все товары указанного бренда (К5)
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Brand, Product
from schemas import BrandSchema, ProductSchema


router = APIRouter(tags=["Brands"])

# ===========================================================================
# Простой in-memory кэш с TTL (общий паттерн из products.py)
# ===========================================================================

_cache: dict[str, tuple[float, Any]] = {}
_TTL = 300.0  # секунд


def _cache_get(key: str) -> Any | None:
    entry = _cache.get(key)
    if entry is None:
        return None
    ts, value = entry
    if time.monotonic() - ts > _TTL:
        del _cache[key]
        return None
    return value


def _cache_set(key: str, value: Any) -> None:
    _cache[key] = (time.monotonic(), value)


# ===========================================================================
# Эндпоинты
# ===========================================================================


@router.get("/brands/", response_model=list[BrandSchema])
async def get_brands(db: Session = Depends(get_db)) -> list[BrandSchema]:
    """Вернуть список всех брендов (К5).

    Результат кэшируется на 5 минут.
    """
    cached = _cache_get("all_brands")
    if cached is not None:
        return cached

    brands = db.query(Brand).order_by(Brand.name).all()
    result = [BrandSchema.model_validate(b) for b in brands]
    _cache_set("all_brands", result)
    return result


@router.get("/brand/{brand_name}", response_model=list[ProductSchema])
async def get_by_brand(
    brand_name: str,
    db: Session = Depends(get_db),
) -> list[ProductSchema]:
    """Вернуть все товары указанного бренда (К5).

    Результат кэшируется на 5 минут.
    """
    cache_key = f"brand:{brand_name}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    brand = (
        db.query(Brand)
        .filter(func.lower(Brand.name) == brand_name.lower())
        .first()
    )
    if brand is None:
        raise HTTPException(
            status_code=404,
            detail=f"Бренд '{brand_name}' не найден.",
        )

    products = (
        db.query(Product)
        .options(
            joinedload(Product.brand),
            joinedload(Product.category),
            joinedload(Product.reviews),
        )
        .filter(Product.brand_id == brand.id)
        .order_by(Product.id)
        .all()
    )

    result = [ProductSchema.model_validate(p) for p in products]
    _cache_set(cache_key, result)
    return result
