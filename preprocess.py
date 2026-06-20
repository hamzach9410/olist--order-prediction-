import pandas as pd
import numpy as np


def load_and_merge(data_dir="./"):
    df = pd.read_csv(f"{data_dir}/orders.csv")

    # keep delivered orders only
    df = df[df["order_status"] == "delivered"].copy()

    # parse timestamps
    for col in ["order_purchase_timestamp", "order_delivered_customer_date",
                "order_approved_at", "order_delivered_carrier_date",
                "order_estimated_delivery_date"]:
        df[col] = pd.to_datetime(df[col])

    # target
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days

    # temporal features
    df["order_hour"]  = df["order_purchase_timestamp"].dt.hour
    df["order_dow"]   = df["order_purchase_timestamp"].dt.dayofweek
    df["order_month"] = df["order_purchase_timestamp"].dt.month

    df["approval_delay"] = (
        df["order_approved_at"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 3600  # hours

    df["estimated_days"] = (
        df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]
    ).dt.days

    df["carrier_pickup_delay"] = (
        df["order_delivered_carrier_date"] - df["order_approved_at"]
    ).dt.total_seconds() / 3600  # hours

    # extra engineered features
    df["is_weekend"]    = df["order_dow"].isin([5, 6]).astype(int)
    df["is_night_order"] = df["order_hour"].between(20, 23).astype(int)

    # ratio: how much of estimated window is already used by carrier pickup
    df["carrier_to_estimated_ratio"] = (
        df["carrier_pickup_delay"] / (df["estimated_days"] * 24)
    ).clip(0, 5)  # cap outliers

    df = df.dropna(subset=["delivery_days"])
    df = df[df["delivery_days"] > 0]

    return df


if __name__ == "__main__":
    df = load_and_merge()
    print(df.shape)
    print(df["delivery_days"].describe())
    df.to_csv("./data/merged.csv", index=False)
    print("Saved ./data/merged.csv")
