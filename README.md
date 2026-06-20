# 🚚 Olist Order Delivery ETA Predictor

An end-to-end MLOps project that predicts e-commerce delivery time using **96,000+ real Brazilian orders** from Olist. Built with LightGBM, MLflow, Apache Kafka, and FastAPI.

---

## 🧠 What This Project Does

When a customer places an order online, they want to know: **"When will it arrive?"**

This system answers that question in real-time using a trained ML model. It simulates a production ML pipeline:

```
Raw Orders (CSV)
      ↓
Feature Engineering (preprocess.py)
      ↓
LightGBM Model Training + MLflow Tracking (train.py)
      ↓
Model registered in MLflow Model Registry
      ↓
Kafka Producer streams order events → Kafka Topic
      ↓
Kafka Consumer reads events → runs ML inference → publishes predictions
      ↓
FastAPI serves predictions via REST API + Web UI
```

---

## 📊 Model Results

| Metric | Value |
|--------|-------|
| Dataset | 96,457 delivered orders |
| Model | LightGBM Regressor |
| MAE | ~4.70 days |
| RMSE | ~8.03 days |
| R² | ~0.41 |
| Avg Delivery Time | 12.1 days |

---

## 🗂️ Project Structure

```
olist-delivery-eta/
├── orders.csv                 ← Raw Olist dataset (96k orders)
├── preprocess.py              ← Feature engineering → data/merged.csv
├── train.py                   ← LightGBM training + MLflow logging
├── model.pkl                  ← Saved model artifact
├── docker-compose.yml         ← Kafka + Zookeeper containers
├── kafka_producer.py          ← Streams orders into Kafka topic
├── kafka_consumer.py          ← Reads orders, runs inference, publishes predictions
├── api/
│   └── main.py                ← FastAPI prediction endpoint + Web UI
├── data/
│   └── merged.csv             ← Preprocessed feature dataset
├── neo4j/
│   ├── ingest.py              ← Bulk ETL into Neo4j AuraDB
│   ├── queries.py             ← Analytics Cypher queries
│   └── demo_queries.cypher    ← 10 demo Cypher queries
├── notebooks/
│   └── demo.ipynb             ← EDA + model evaluation + Neo4j charts
└── requirements.txt
```

---

## ⚙️ Tech Stack

| Tool | Role |
|------|------|
| **LightGBM** | Gradient boosting regression model |
| **MLflow** | Experiment tracking, model registry |
| **Apache Kafka** | Real-time order event streaming |
| **FastAPI** | REST API + Web UI frontend |
| **Neo4j AuraDB** | Graph database — Customer→Order relationships |
| **Docker** | Runs Kafka + Zookeeper containers |
| **pandas / scikit-learn** | Data processing & evaluation |

---

## 🚀 How to Run (Step by Step)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MLflow Tracking Server
Open **Terminal 1**:
```bash
cd olist-delivery-eta
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```
✅ Open → http://localhost:5000

---

### 3. Train the Model
Open **Terminal 2**:
```bash
cd olist-delivery-eta
python train.py
```
This will:
- Load `data/merged.csv`
- Train LightGBM with 500 estimators
- Log MAE, RMSE, R² to MLflow
- Register model as `OlistDeliveryModel` in MLflow Registry

✅ After training, go to http://localhost:5000 → Models → `OlistDeliveryModel` → set version to **Production**

---

### 4. Start FastAPI (Web UI + API)
Open **Terminal 3**:
```bash
cd olist-delivery-eta
python -m uvicorn api.main:app --reload --port 8000
```
✅ Open → http://localhost:8000 (Web UI)
✅ Open → http://localhost:8000/docs (Swagger API docs)

---

### 5. Start Kafka (Docker required)
Make sure **Docker Desktop is running**, then open **Terminal 4**:
```bash
cd olist-delivery-eta
docker-compose up -d
```

---

### 6. Start Kafka Consumer (ML Inference)
Open **Terminal 5**:
```bash
cd olist-delivery-eta
python kafka_consumer.py
```
This loads the Production model from MLflow and waits for incoming order events.

---

### 7. Start Kafka Producer (Stream Orders)
Open **Terminal 6**:
```bash
cd olist-delivery-eta
python kafka_producer.py
```
This streams the first 100 orders from `data/merged.csv` into the `unprocessed-orders` Kafka topic — one order per second.

Watch **Terminal 5** for live predictions like:
```
[PREDICTION] Order abc123 -> Estimated Delivery: 8.24 days
```

---

## 🌐 API Usage

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
  "approval_delay": 0.5,
  "estimated_days": 10,
  "carrier_pickup_delay": 2.0,
  "is_weekend": 0,
  "is_night_order": 0,
  "carrier_to_estimated_ratio": 0.2
}
```

**Response:**
```json
{
  "predicted_delivery_days": 8.3
}
```

---

## 🔧 Feature Engineering

| Feature | Description |
|---------|-------------|
| `estimated_days` | Seller-promised delivery window (days) |
| `approval_delay` | Hours from purchase to order approval |
| `carrier_pickup_delay` | Hours from approval to carrier pickup |
| `carrier_to_estimated_ratio` | Pickup delay as fraction of estimated window |
| `order_hour` | Hour of purchase (0–23) |
| `order_dow` | Day of week (0=Monday) |
| `order_month` | Month of purchase (1–12) |
| `is_weekend` | 1 if order placed on Sat/Sun |
| `is_night_order` | 1 if order placed between 8pm–11pm |

---

## 📈 MLflow Tracking

Every training run logs:
- **Parameters:** n_estimators, learning_rate, num_leaves
- **Metrics:** MAE, RMSE, R²
- **Model:** registered as `OlistDeliveryModel` in Model Registry
- **Tags:** feature list used for training

---

## 🔗 Neo4j Graph Schema

```
(Customer)-[:PLACED]->(Order)
```

**Order properties:** `delivery_days`, `estimated_days`, `order_month`, `order_dow`, `approval_delay_hrs`, `status`

Run demo queries in Neo4j Browser → https://console.neo4j.io

---

## 💡 Key Insights from Data

- Orders from SP → distant states take 2–3x longer
- Carrier pickup delay is the strongest predictor of late delivery
- Weekend orders average ~1.5 days longer
- November (Black Friday) shows the highest late delivery rate
- Orders placed at night get approved ~3hrs later on average

---

## 📦 Suggested Repo Names

Here are some good options:

| Name | Why |
|------|-----|
| `olist-delivery-eta` | Simple and descriptive |
| `ml-delivery-predictor` | Highlights the ML angle |
| `ecommerce-eta-mlops` | Highlights the MLOps stack |
| **`olist-mlops-pipeline`** ⭐ | Best for portfolio — shows full pipeline |
| `realtime-delivery-prediction` | Highlights Kafka streaming |

> ⭐ Recommended: **`olist-mlops-pipeline`** — it tells recruiters exactly what you built.

---

## 👤 Author

Built as an end-to-end MLOps portfolio project demonstrating real-time ML inference with industry-standard tools.
