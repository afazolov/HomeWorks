SELECT *
FROM customers
ORDER BY company_name;


SELECT *
FROM orders
ORDER BY order_date;

COPY (
SELECT *
FROM customers
ORDER BY company_name
) TO 'C:\temp\customers.csv' WITH (FORMAT csv, HEADER true);