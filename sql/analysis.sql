-- Revenue by product category
SELECT category, ROUND(SUM(revenue), 2) AS total_revenue
FROM sales GROUP BY category ORDER BY total_revenue DESC;

-- Monthly revenue
SELECT substr(order_date, 1, 7) AS month, ROUND(SUM(revenue), 2) AS revenue
FROM sales GROUP BY month ORDER BY month;

-- Top customers by revenue
SELECT customer_id, ROUND(SUM(revenue), 2) AS lifetime_revenue
FROM sales GROUP BY customer_id ORDER BY lifetime_revenue DESC;
