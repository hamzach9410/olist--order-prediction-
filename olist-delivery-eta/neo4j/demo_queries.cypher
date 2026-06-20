// ============================================================
// Olist Delivery ETA — Neo4j Demo Queries
// Run these in Neo4j Browser: https://console.neo4j.io
// ============================================================

// 1. Total nodes in graph
MATCH (n)
RETURN labels(n)[0] AS type, count(n) AS total
ORDER BY total DESC;

// 2. Average delivery days by month
MATCH (o:Order)
RETURN o.order_month AS month,
       round(avg(o.delivery_days), 1) AS avg_days,
       count(o) AS orders
ORDER BY month;

// 3. Late orders (delivered after estimate)
MATCH (o:Order)
WHERE o.delivery_days > o.estimated_days
RETURN count(o) AS late_orders;

// 4. On-time vs late breakdown
MATCH (o:Order)
RETURN
  CASE WHEN o.delivery_days > o.estimated_days THEN 'Late' ELSE 'On Time' END AS status,
  count(o) AS orders,
  round(avg(o.delivery_days), 1) AS avg_days;

// 5. Customers with most orders
MATCH (c:Customer)-[:PLACED]->(o:Order)
RETURN c.id AS customer, count(o) AS total_orders
ORDER BY total_orders DESC
LIMIT 10;

// 6. Slowest delivery month
MATCH (o:Order)
RETURN o.order_month AS month,
       round(avg(o.delivery_days), 1) AS avg_days
ORDER BY avg_days DESC
LIMIT 1;

// 7. Orders delivered in under 5 days (fast deliveries)
MATCH (c:Customer)-[:PLACED]->(o:Order)
WHERE o.delivery_days <= 5
RETURN count(o) AS fast_orders,
       round(avg(o.delivery_days), 1) AS avg_days;

// 8. Orders taking more than 30 days (very slow)
MATCH (c:Customer)-[:PLACED]->(o:Order)
WHERE o.delivery_days > 30
RETURN count(o) AS very_slow_orders;

// 9. Approval delay vs delivery days correlation
MATCH (o:Order)
WHERE o.approval_delay_hrs IS NOT NULL
RETURN
  CASE
    WHEN o.approval_delay_hrs < 1  THEN 'Under 1hr'
    WHEN o.approval_delay_hrs < 24 THEN '1-24hrs'
    ELSE 'Over 24hrs'
  END AS approval_bucket,
  count(o) AS orders,
  round(avg(o.delivery_days), 1) AS avg_delivery_days
ORDER BY avg_delivery_days;

// 10. Weekend vs weekday orders
MATCH (o:Order)
RETURN
  CASE WHEN o.order_dow IN [5,6] THEN 'Weekend' ELSE 'Weekday' END AS order_type,
  count(o) AS orders,
  round(avg(o.delivery_days), 1) AS avg_days;
