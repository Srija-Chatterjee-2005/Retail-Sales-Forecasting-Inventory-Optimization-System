import pandas as pd

def preprocess_data(file_path):
    df = pd.read_csv(file_path, parse_dates=["date"])

    df = df.drop_duplicates(subset=["date", "store_id", "item_id"])
    df = df.sort_values(["store_id", "item_id", "date"]).reset_index(drop=True)

    numeric_cols = [
        "price", "discount_pct", "qty_sold", "stock_on_hand",
        "supplier_lead_time_days", "unit_cost", "holding_cost_rate", "ordering_cost"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["on_promo"] = df["on_promo"].fillna(0).astype(int)
    df["stockout_flag"] = df["stockout_flag"].fillna(0).astype(int)

    df["discount_pct"] = df["discount_pct"].fillna(0)
    df["price"] = df["price"].fillna(df["price"].median())
    df["qty_sold"] = df["qty_sold"].fillna(0)
    df["stock_on_hand"] = df["stock_on_hand"].ffill()

    df["qty_sold"] = df["qty_sold"].clip(lower=0)
    df["stock_on_hand"] = df["stock_on_hand"].clip(lower=0)

    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    return df