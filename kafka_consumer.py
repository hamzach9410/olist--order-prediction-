import json
import pandas as pd
import mlflow.lightgbm
from confluent_kafka import Consumer, Producer
import os

# MLflow configuration
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))

# Dynamic Model Loading from Model Registry
model_uri = "models:/OlistDeliveryModel/Production"
try:
    print(f"Loading model from {model_uri}...")
    model = mlflow.lightgbm.load_model(model_uri)
    print("Production model loaded successfully.")
except Exception as e:
    print(f"Could not load model: {e}")
    print("Ensure MLflow is running and 'OlistDeliveryModel' has a 'Production' version.")
    model = None

# We use the same features the model was trained on
FEATURES = [
    "order_hour", "order_dow", "order_month",
    "approval_delay", "estimated_days", "carrier_pickup_delay",
    "is_weekend", "is_night_order",
    "carrier_to_estimated_ratio",
]

def delivery_report(err, msg):
    if err is not None:
        print(f"Prediction delivery failed: {err}")
    else:
        print(f"Prediction delivered to {msg.topic()} [{msg.partition()}]")

def run_consumer():
    consumer_conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'ml-prediction-group',
        'auto.offset.reset': 'earliest'
    }
    producer_conf = {'bootstrap.servers': 'localhost:9092'}
    
    consumer = Consumer(consumer_conf)
    producer = Producer(producer_conf)
    
    consumer.subscribe(['unprocessed-orders'])
    print("Consumer started. Waiting for order events...")
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
                
            event = json.loads(msg.value().decode('utf-8'))
            order_id = event.get('order_id', 'unknown')
            
            if model is not None:
                # Structure data for prediction
                df = pd.DataFrame([event])
                for f in FEATURES:
                    if f not in df.columns:
                        df[f] = 0.0
                X = df[FEATURES]
                
                # Perform inference
                preds = model.predict(X)
                eta = float(preds[0])
                
                print(f"[PREDICTION] Order {order_id} -> Estimated Delivery: {eta:.2f} days")
                
                # Publish enriched output
                result_event = {
                    "order_id": order_id,
                    "predicted_eta_days": eta
                }
                producer.produce('order-predictions', key=str(order_id), value=json.dumps(result_event), callback=delivery_report)
                producer.poll(0)
            else:
                print(f"Order {order_id} ignored: MLflow model not available.")

    except KeyboardInterrupt:
        print("\nStopping consumer...")
    finally:
        consumer.close()
        producer.flush()

if __name__ == '__main__':
    run_consumer()
