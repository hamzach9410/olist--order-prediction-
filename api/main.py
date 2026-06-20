from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.lightgbm
import pandas as pd
import numpy as np
from pathlib import Path
import os

app = FastAPI(title="Olist Delivery ETA API")

@app.get("/")
def read_root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

model   = None
COLUMNS = [
    "order_hour", "order_dow", "order_month",
    "approval_delay", "estimated_days", "carrier_pickup_delay",
    "is_weekend", "is_night_order",
    "carrier_to_estimated_ratio",
]

def load_model():
    global model
    if model is None:
        try:
            mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
            model_uri = "models:/OlistDeliveryModel/Production"
            model = mlflow.lightgbm.load_model(model_uri)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Model not loaded from MLflow: {str(e)}")

class OrderInput(BaseModel):
    freight_value: float
    price: float
    n_items: int = 1
    customer_state: str
    seller_state: str
    product_category_name: str
    order_hour: int = 12
    order_dow: int = 1
    order_month: int = 6
    approval_delay: float = 1.0
    estimated_days: float = 10.0
    carrier_pickup_delay: float = 2.0
    is_weekend: int = 0
    is_night_order: int = 0
    carrier_to_estimated_ratio: float = 0.2

@app.post("/predict")
def predict(order: OrderInput):
    load_model()
    row = pd.DataFrame([order.model_dump()])
    X   = row.reindex(columns=COLUMNS, fill_value=0)

    days = float(np.round(model.predict(X)[0], 1))
    return {"predicted_delivery_days": days}

@app.get("/health")
def health():
    return {"status": "ok"}
