"""
Copy .env.example to .env and fill in your Neo4j AuraDB credentials.
This file is safe to commit — credentials are loaded from environment.
"""
import pandas as pd
from neo4j import GraphDatabase
import os

NEO4J_URI  = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASS = os.getenv("NEO4J_PASS")

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS FOR (c:Customer) ON (c.id)",
    "CREATE INDEX IF NOT EXISTS FOR (o:Order)    ON (o.id)",
]

INGEST_QUERY = """
UNWIND $rows AS row
MERGE (c:Customer {id: row.customer_id})
MERGE (o:Order    {id: row.order_id})
  SET o.delivery_days      = row.delivery_days,
      o.order_month        = row.order_month,
      o.order_dow          = row.order_dow,
      o.approval_delay_hrs = row.approval_delay,
      o.estimated_days     = row.estimated_days,
      o.status             = row.order_status
MERGE (c)-[:PLACED]->(o)
"""

def ingest(data_path="./data/merged.csv", batch_size=2000):
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASS]):
        raise ValueError("Set NEO4J_URI, NEO4J_USER, NEO4J_PASS in your .env file")

    df = pd.read_csv(data_path).fillna("unknown")
    records = df[[
        "customer_id", "order_id", "order_status",
        "delivery_days", "order_month", "order_dow",
        "approval_delay", "estimated_days",
    ]].to_dict("records")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    with driver.session() as session:
        for q in CREATE_INDEXES:
            session.run(q)
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            session.run(INGEST_QUERY, rows=batch)
            print(f"Inserted {min(i+batch_size, len(records))}/{len(records)}")

    driver.close()
    print("Neo4j ingestion complete.")


if __name__ == "__main__":
    ingest()
