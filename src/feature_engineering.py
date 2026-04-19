import pandas as pd

def add_lag_features(df, group_cols=["store_id", "item_id"], target_col="qty_sold"):
    df = df.copy()
    df = df.sort_values(group_cols + ["date"]).reset_index(drop=True)

    grouped = df.groupby(group_cols)[target_col]

    # Lag features
    for lag in [1, 7, 14]:
        df[f"lag_{lag}"] = grouped.shift(lag)

    # Rolling mean features
    for window in [7, 14, 28]:
        df[f"rolling_mean_{window}"] = grouped.transform(
            lambda x: x.shift(1).rolling(window=window).mean()
        )
        df[f"rolling_std_{window}"] = grouped.transform(
            lambda x: x.shift(1).rolling(window=window).std()
        )

    return df