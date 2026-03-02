-- =============================================================================
-- Продвинутый Python — Итоговый проект
-- Файл: schema.sql
-- Назначение: создание схемы БД (3NF) для каталога товаров DummyJSON.
--
-- Запуск:
--     psql -U postgres -d synergy -f schema.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Справочник брендов
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS brands (
    id   SERIAL       PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_brands_name ON brands (name);

-- -----------------------------------------------------------------------------
-- Справочник категорий
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id   SERIAL       PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories (name);

-- -----------------------------------------------------------------------------
-- Товары (SKU)
-- Внешние ключи: brand_id → brands.id, category_id → categories.id
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY,           -- id из DummyJSON
    title       VARCHAR(512) NOT NULL,
    description TEXT,
    price       FLOAT        NOT NULL,
    stock       INTEGER      NOT NULL DEFAULT 0,
    rating      FLOAT,
    thumbnail   TEXT,
    brand_id    INTEGER REFERENCES brands(id)     ON DELETE SET NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_products_brand_id    ON products (brand_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products (category_id);

-- -----------------------------------------------------------------------------
-- Отзывы к товарам
-- Внешний ключ: product_id → products.id (CASCADE DELETE)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    id             SERIAL       PRIMARY KEY,
    product_id     INTEGER      NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    rating         FLOAT,
    comment        TEXT,
    reviewer_name  VARCHAR(255),
    reviewer_email VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews (product_id);
