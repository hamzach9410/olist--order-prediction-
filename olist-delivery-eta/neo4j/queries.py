"""
Useful Cypher analytics queries — run in Neo4j Browser (http://localhost:7474)
"""

QUERIES = {
    "slowest_sellers": """
        MATCH (o:Order)-[:SHIPPED_BY]->(s:Seller)
        RETURN s.id AS seller, s.state AS state,
               round(avg(o.delivery_days), 1) AS avg_days,
               count(o) AS total_orders
        ORDER BY avg_days DESC
        LIMIT 10
    """,

    "fastest_sellers": """
        MATCH (o:Order)-[:SHIPPED_BY]->(s:Seller)
        RETURN s.id AS seller, s.state AS state,
               round(avg(o.delivery_days), 1) AS avg_days,
               count(o) AS total_orders
        ORDER BY avg_days ASC
        LIMIT 10
    """,

    "delay_by_customer_state": """
        MATCH (c:Customer)-[:PLACED]->(o:Order)
        RETURN c.state AS state,
               round(avg(o.delivery_days), 1) AS avg_days,
               count(o) AS orders
        ORDER BY avg_days DESC
    """,

    "delay_by_product_category": """
        MATCH (o:Order)
        WHERE o.product_category <> 'unknown'
        RETURN o.product_category AS category,
               round(avg(o.delivery_days), 1) AS avg_days,
               count(o) AS orders
        ORDER BY avg_days DESC
        LIMIT 15
    """,

    "high_value_slow_orders": """
        MATCH (c:Customer)-[:PLACED]->(o:Order)-[:SHIPPED_BY]->(s:Seller)
        WHERE o.delivery_days > 20 AND o.price > 300
        RETURN c.id, o.id, o.delivery_days, o.price, s.state
        LIMIT 20
    """,

    "seller_customer_cross_state": """
        MATCH (c:Customer)-[:PLACED]->(o:Order)-[:SHIPPED_BY]->(s:Seller)
        WHERE c.state <> s.state
        RETURN c.state AS from_state, s.state AS to_state,
               round(avg(o.delivery_days), 1) AS avg_days,
               count(o) AS orders
        ORDER BY avg_days DESC
        LIMIT 15
    """,
}

if __name__ == "__main__":
    for name, q in QUERIES.items():
        print(f"\n--- {name} ---")
        print(q.strip())
