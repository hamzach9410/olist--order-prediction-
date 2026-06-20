import pandas as pd
import json
import time
from confluent_kafka import Producer

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def run_producer():
    conf = {'bootstrap.servers': 'localhost:9092'}
    producer = Producer(conf)
    topic = 'unprocessed-orders'

    try:
        # Load preprocessed data to simulate streaming
        df = pd.read_csv('./data/merged.csv')
        
        print("Starting Kafka Producer...")
        # We will simulate streaming the first 100 orders
        for index, row in df.head(100).iterrows():
            order_event = row.to_dict()
            
            # Serialize to JSON
            payload = json.dumps(order_event)
            order_id = str(order_event.get('order_id', index))
            
            producer.produce(topic, key=order_id, value=payload, callback=delivery_report)
            producer.poll(0)
            
            # Simulate streaming delay
            time.sleep(1)

    except FileNotFoundError:
        print("Error: ./data/merged.csv not found. Run preprocess.py first.")
    except Exception as e:
        print(f"Producer error: {e}")
    finally:
        producer.flush()
        print("Producer finished streaming events.")

if __name__ == '__main__':
    run_producer()
