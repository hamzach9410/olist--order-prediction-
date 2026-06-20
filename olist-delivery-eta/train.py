import pandas as pd
import numpy as np
import mlflow
import mlflow.lightgbm
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

FEATURES = [
    "order_hour", "order_dow", "order_month",
    "approval_delay", "estimated_days", "carrier_pickup_delay",
    "is_weekend", "is_night_order",
    "carrier_to_estimated_ratio",
]

def train(data_path="./data/merged.csv"):
    df = pd.read_csv(data_path)
    df = df.dropna(subset=FEATURES + ["delivery_days"])

    X = df[FEATURES]
    y = df["delivery_days"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # MLflow Setup
    mlflow.set_tracking_uri("http://localhost:5000")  # Configure remote or local MLflow tracking server
    mlflow.set_experiment("Olist_Delivery_ETA")

    with mlflow.start_run() as run:
        # Define Hyperparameters
        params = {
            "n_estimators": 500,
            "learning_rate": 0.05,
            "num_leaves": 63,
            "random_state": 42
        }
        
        # Log Hyperparameters
        mlflow.log_params(params)

        model = LGBMRegressor(**params)
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            callbacks=[__import__("lightgbm").early_stopping(50, verbose=False)],
        )

        # Predictions & Metrics
        preds = model.predict(X_test)
        mae  = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        
        print(f"MAE : {mae:.2f} days")
        print(f"RMSE: {rmse:.2f} days")
        print(f"R2  : {r2:.2f}")

        # Log Metrics
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        # Log Model & Register to Model Registry
        # We also pass the FEATURES list as part of the model's metadata or input example,
        # but storing it in tags or artifacts is cleaner. 
        mlflow.set_tag("features", ",".join(FEATURES))
        
        mlflow.lightgbm.log_model(
            lgb_model=model,
            artifact_path="model",
            registered_model_name="OlistDeliveryModel"
        )
        print(f"Model saved and registered to MLflow. Run ID: {run.info.run_id}")

    return model

if __name__ == "__main__":
    train()
