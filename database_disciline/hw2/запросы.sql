SELECT * FROM orders LIMIT 5;

SELECT
ship_city AS city,
COUNT(*) AS orders_count
FROM orders
GROUP BY ship_city
ORDER BY orders_count DESC, city;

COPY (
SELECT
ship_city AS city,
COUNT(*) AS orders_count
FROM orders
GROUP BY ship_city
ORDER BY orders_count DESC, city
) TO 'C:\temp\orders_by_city.csv' WITH (FORMAT csv, HEADER true);


SELECT * FROM customers LIMIT 5;

SELECT
country,
COUNT(*) AS customers_count
FROM customers
GROUP BY country
ORDER BY customers_count DESC, country;

COPY (
SELECT
country,
COUNT(*) AS customers_count
FROM customers
GROUP BY country
ORDER BY customers_count DESC, country
) TO 'C:\temp\customers_by_country.csv' WITH (FORMAT csv, HEADER true);

SELECT
c.country,
EXTRACT(YEAR FROM o.order_date) AS year,
COUNT(*) AS orders_count
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country, EXTRACT(YEAR FROM o.order_date)
ORDER BY c.country, year;

COPY (
SELECT
c.country,
EXTRACT(YEAR FROM o.order_date) AS year,
COUNT(*) AS orders_count
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country, EXTRACT(YEAR FROM o.order_date)
ORDER BY c.country, year
) TO 'C:\temp\orders_by_year_country.csv' WITH (FORMAT csv, HEADER true);