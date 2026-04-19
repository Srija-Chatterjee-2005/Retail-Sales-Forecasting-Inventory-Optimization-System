import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.feature_engineering import add_lag_features

MODEL_FEATURES = [
    "price", "on_promo", "discount_pct", "stock_on_hand",
    "supplier_lead_time_days", "day_of_week", "month", "week_of_year", "is_weekend",
    "lag_1", "lag_7", "lag_14",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
    "rolling_std_7", "rolling_std_14", "rolling_std_28"
]

def train_and_evaluate_model(df):
    df_feat = add_lag_features(df)
    df_feat = df_feat.dropna().reset_index(drop=True)

    split_date = df_feat["date"].quantile(0.8)

    train_df = df_feat[df_feat["date"] <= split_date].copy()
    test_df = df_feat[df_feat["date"] > split_date].copy()

    X_train = train_df[MODEL_FEATURES]
    y_train = train_df["qty_sold"]

    X_test = test_df[MODEL_FEATURES]
    y_test = test_df["qty_sold"]

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    preds = np.maximum(0, preds)

    metrics = {
        "MAE": round(mean_absolute_error(y_test, preds), 4),
        "RMSE": round(np.sqrt(mean_squared_error(y_test, preds)), 4),
        "R2_SCORE": round(r2_score(y_test, preds), 4)
    }

    metrics_df = pd.DataFrame([metrics])
    return metrics_df, df_feat

def recursive_forecast_for_sku_store(df, selected_store, selected_item, horizon=7):
    df = df.copy()
    subset = df[
        (df["store_id"] == selected_store) &
        (df["item_id"] == selected_item)
    ].sort_values("date").copy()

    subset = add_lag_features(subset, group_cols=["store_id", "item_id"])
    subset = subset.dropna().reset_index(drop=True)

    if subset.empty:
        return pd.DataFrame(columns=["date", "forecast_qty"])

    # train on this sku-store subset
    usable = subset.dropna(subset=MODEL_FEATURES + ["qty_sold"]).copy()
    X = usable[MODEL_FEATURES]
    y = usable["qty_sold"]

    model = RandomForestRegressor(
        n_estimators=120,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X, y)

    future_rows = []
    history = subset.copy()
    last_date = history["date"].max()

    for step in range(1, horizon + 1):
        next_date = last_date + pd.Timedelta(days=1)

        row = history.iloc[-1:].copy()
        row["date"] = next_date
        row["day_of_week"] = next_date.dayofweek
        row["month"] = next_date.month
        row["week_of_year"] = int(next_date.isocalendar().week)
        row["is_weekend"] = 1 if next_date.dayofweek in [5, 6] else 0
        row["on_promo"] = 0
        row["discount_pct"] = 0

        temp = pd.concat([history, row], ignore_index=True)
        temp = add_lag_features(temp, group_cols=["store_id", "item_id"])
        candidate = temp.iloc[-1:].copy()

        X_future = candidate[MODEL_FEATURES].fillna(0)
        pred = float(model.predict(X_future)[0])
        pred = max(0, round(pred, 2))

        candidate["qty_sold"] = pred
        history = pd.concat([history, candidate], ignore_index=True)

        future_rows.append({
            "date": next_date,
            "forecast_qty": pred
        })

        last_date = next_date

    return pd.DataFrame(future_rows)

def generate_inventory_ready_dataset(df):
    grouped = df.groupby(["store_id", "item_id"], as_index=False).agg(
        avg_daily_sales=("qty_sold", "mean"),
        avg_stock=("stock_on_hand", "mean"),
        avg_lead_time=("supplier_lead_time_days", "mean")
    )
    return grouped