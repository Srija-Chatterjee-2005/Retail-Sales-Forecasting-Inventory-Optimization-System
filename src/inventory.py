import numpy as np
import pandas as pd
from scipy.stats import norm
from src.forecasting import recursive_forecast_for_sku_store

def inventory_policy(
    forecast_values,
    current_stock,
    lead_time,
    service_level=0.95,
    annual_demand=10000,
    ordering_cost=500,
    unit_cost=100,
    holding_cost_rate=0.18,
    residual_std=5
):
    z = norm.ppf(service_level)

    lead_time = int(max(1, round(lead_time)))
    demand_during_lead = np.sum(forecast_values[:lead_time])

    sigma_lead = residual_std * np.sqrt(lead_time)
    safety_stock = z * sigma_lead
    reorder_point = demand_during_lead + safety_stock

    holding_cost = unit_cost * holding_cost_rate
    eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost) if holding_cost > 0 else demand_during_lead

    recommended_order_qty = max(0, round(max(eoq, reorder_point - current_stock), 2))

    return {
        "forecast_demand_during_lead_time": round(demand_during_lead, 2),
        "safety_stock": round(safety_stock, 2),
        "reorder_point": round(reorder_point, 2),
        "economic_order_quantity": round(eoq, 2),
        "recommended_order_qty": round(recommended_order_qty, 2)
    }

def compute_inventory_table(sales_df, forecast_df, selected_store, selected_item):
    subset = sales_df[
        (sales_df["store_id"] == selected_store) &
        (sales_df["item_id"] == selected_item)
    ].sort_values("date")

    if subset.empty or forecast_df.empty:
        return pd.DataFrame()

    latest = subset.iloc[-1]
    current_stock = latest["stock_on_hand"]
    lead_time = latest["supplier_lead_time_days"]
    unit_cost = latest["unit_cost"]
    holding_cost_rate = latest["holding_cost_rate"]
    ordering_cost = latest["ordering_cost"]

    annual_demand = subset["qty_sold"].sum() / max(1, subset["date"].dt.year.nunique())
    residual_std = max(1, subset["qty_sold"].std())

    policy = inventory_policy(
        forecast_values=forecast_df["forecast_qty"].values,
        current_stock=current_stock,
        lead_time=lead_time,
        annual_demand=annual_demand,
        ordering_cost=ordering_cost,
        unit_cost=unit_cost,
        holding_cost_rate=holding_cost_rate,
        residual_std=residual_std
    )

    result = {
        "store_id": selected_store,
        "item_id": selected_item,
        "current_stock": round(current_stock, 2),
        "lead_time_days": int(lead_time),
        **policy
    }

    return pd.DataFrame([result])

def build_full_inventory_recommendations(df):
    rows = []
    unique_pairs = df[["store_id", "item_id"]].drop_duplicates()

    for _, pair in unique_pairs.iterrows():
        store = pair["store_id"]
        item = pair["item_id"]

        forecast_df = recursive_forecast_for_sku_store(df, store, item, horizon=7)
        table = compute_inventory_table(df, forecast_df, store, item)

        if not table.empty:
            rows.append(table.iloc[0].to_dict())

    return pd.DataFrame(rows)