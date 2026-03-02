"""
Продвинутый Python — Итоговый проект
-------------------------------------
Роутер: statistics.py
Эндпоинт:
    GET /statistics/   — сводная статистика по каталогу
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from database import get_db
from models import Brand, Category, Product, Review
from schemas import StatisticsSchema


router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get("/", response_model=StatisticsSchema)
async def get_statistics(db: Session = Depends(get_db)) -> StatisticsSchema:
    """Вернуть сводную статистику по каталогу товаров.

    Оптимизировано: агрегация products выполняется одним запросом (CASE).
    """
    # Один запрос для total и low_stock (оптимизация из конспекта)
    product_stats = db.query(
        func.count(Product.id).label("total"),
        func.sum(
            case((Product.stock < 10, 1), else_=0)
        ).label("low_stock"),
        func.avg(Product.price).label("avg_price"),
    ).first()

    total_brands     = db.query(func.count(Brand.id)).scalar() or 0
    total_categories = db.query(func.count(Category.id)).scalar() or 0
    total_reviews    = db.query(func.count(Review.id)).scalar() or 0

    return StatisticsSchema(
        total_products     = product_stats.total     or 0,
        low_stock_products = product_stats.low_stock or 0,
        avg_price          = round(product_stats.avg_price, 2) if product_stats.avg_price else None,
        total_brands       = total_brands,
        total_categories   = total_categories,
        total_reviews      = total_reviews,
    )
