# Olist Delivery ETA Predictor

Predict e-commerce delivery time using the **Olist Brazil dataset** (96k real orders).
This project features an event-driven architecture using **Apache Kafka**, model lifecycle management with **MLflow**, a **LightGBM regression model**, and exploratory relationship analytics via a **Neo4j property graph**.

---

## Results

| Metric | Value |
|--------|-------|
| Dataset | 96,457 delivered orders |
| Model | LightGBM Regressor |
| MAE | ~4.70 days |
| RMSE | ~8.03 days |
| Avg delivery time | 12.1 days |

---

## Project Structure

```
olist-delivery-eta/
├── orders.csv              ← Olist raw dataset
├── data/
│   └── merged.csv          ← Preprocessed features
├── preprocess.py           ← Feature engineering
├── train.py                ← LightGBM training & MLflow logging
├── kafka_producer.py       ← Streams new orders to Kafka
├── kafka_consumer.py       ← Consumes orders & predicts ETA using MLflow model
├── neo4j/
│   ├── ingest.py           ← Bulk ETL into Neo4j AuraDB
│   ├── queries.py          ← Analytics queries
│   └── demo_queries.cypher ← 10 demo Cypher queries
├── api/
│   └── main.py             ← FastAPI prediction endpoint (Dynamically loads model from MLflow)
├── notebooks/
│   └── demo.ipynb          ← Full EDA + model eval + Neo4j charts
└── requirements.txt
```

---

## Quickstart

```bash
pip install -r requirements.txt

# 1. Feature Engineering
python preprocess.py        # outputs data/merged.csv

# 2. Start MLflow Tracking Server
mlflow server --host 127.0.0.1 --port 5000

# 3. Train Model & Register to MLflow
python train.py             # Trains LightGBM and logs to MLflow Registry

# 4. Start API (loads Production model from MLflow)
uvicorn api.main:app --reload
```

*Note: For event streaming, ensure Apache Kafka is running locally on port 9092, then run `kafka_consumer.py` and `kafka_producer.py`.*

---

## Prediction API

**POST** `http://localhost:8000/predict`

```json
{
  "freight_value": 15.5,
  "price": 89.9,
  "n_items": 2,
  "customer_state": "SP",
  "seller_state": "RJ",
  "product_category_name": "electronics",
  "order_hour": 14,
  "order_dow": 2,
  "order_month": 6,
  "approval_delay": 0.5
}
```

Response:
```json
{"predicted_delivery_days": 8.3}
```

Interactive docs → http://localhost:8000/docs

---

## Neo4j Graph Schema

```
(Customer)-[:PLACED]->(Order)
```

**Order properties:** `delivery_days`, `estimated_days`, `order_month`,
`order_dow`, `approval_delay_hrs`, `status`

**Demo queries** → `neo4j/demo_queries.cypher`
Run in Neo4j Browser → https://console.neo4j.io

Key insights from graph:
- Late delivery rate and on-time breakdown
- Avg delivery days by month (seasonal patterns)
- Approval delay impact on delivery speed
- Weekend vs weekday order patterns

---

## Feature Engineering

| Feature | Description |
|---------|-------------|
| `estimated_days` | Seller-promised delivery window |
| `carrier_pickup_delay` | Hours from approval to carrier pickup |
| `carrier_to_estimated_ratio` | Pickup delay as fraction of estimated window |
| `approval_delay` | Hours from purchase to approval |
| `order_hour / dow / month` | Temporal features |
| `is_weekend / is_night_order` | Binary flags |

---

## Tech Stack

- **Machine Learning**: LightGBM, scikit-learn, pandas
- **MLOps**: MLflow (Tracking & Model Registry)
- **Event Streaming**: Apache Kafka (`confluent-kafka`)
- **Backend**: FastAPI, uvicorn
- **Graph Database**: Neo4j AuraDB
- **Exploration**: Jupyter Notebooks, seaborn, matplotlib
