import numpy as np
import pandas as pd

def generate_retail_data(
    start_date="2022-01-01",
    end_date="2025-04-14",
    stores=None,
    items=None,
    random_seed=42
):
    np.random.seed(random_seed)

    if stores is None:
        stores = [
            "Store_A", "Store_B", "Store_C",
            "Store_D", "Store_E", "Store_F"
        ]

    item_category_map = {
        "Item_101": "Grocery",
        "Item_102": "Beverages",
        "Item_103": "Personal Care",
        "Item_104": "Snacks",
        "Item_105": "Household",
        "Item_106": "Dairy",
        "Item_107": "Bakery",
        "Item_108": "Frozen Foods",
        "Item_109": "Health & Wellness",
        "Item_110": "Baby Care",
        "Item_111": "Cleaning Supplies",
        "Item_112": "Stationery"
    }

    if items is None:
        items = list(item_category_map.keys())

    base_price = {
        "Item_101": 40,
        "Item_102": 25,
        "Item_103": 120,
        "Item_104": 30,
        "Item_105": 180,
        "Item_106": 55,
        "Item_107": 35,
        "Item_108": 140,
        "Item_109": 220,
        "Item_110": 260,
        "Item_111": 90,
        "Item_112": 60
    }

    lead_time_map = {
        "Item_101": 3,
        "Item_102": 4,
        "Item_103": 6,
        "Item_104": 5,
        "Item_105": 7,
        "Item_106": 3,
        "Item_107": 2,
        "Item_108": 6,
        "Item_109": 8,
        "Item_110": 7,
        "Item_111": 5,
        "Item_112": 4
    }

    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    records = []

    for store in stores:
        store_factor = np.random.uniform(0.85, 1.20)

        for item in items:
            item_factor = np.random.uniform(0.75, 1.35)
            stock_level = np.random.randint(180, 420)

            for date in dates:
                dow = date.dayofweek
                month = date.month

                weekend_boost = 1.18 if dow in [5, 6] else 1.0
                festival_boost = 1.28 if month in [10, 11, 12] else 1.0
                summer_boost = 1.20 if month in [4, 5, 6] and item in ["Item_102"] else 1.0
                winter_boost = 1.14 if month in [11, 12, 1] and item in ["Item_106", "Item_108", "Item_109"] else 1.0

                promo_flag = np.random.choice([0, 1], p=[0.78, 0.22])
                discount_pct = (
                    np.random.choice(
                        [0, 5, 10, 15, 20, 25],
                        p=[0.78, 0.05, 0.05, 0.05, 0.04, 0.03]
                    )
                    if promo_flag else 0
                )

                price = base_price[item] * (1 - discount_pct / 100)

                demand_base = (
                    22
                    * store_factor
                    * item_factor
                    * weekend_boost
                    * festival_boost
                    * summer_boost
                    * winter_boost
                )

                trend = 1 + ((date.year - 2022) * 0.03)
                noise = np.random.normal(0, 5)

                qty_sold = max(0, int(demand_base * trend + noise + (promo_flag * 6)))

                stockout_flag = 0
                if stock_level < qty_sold:
                    qty_sold = stock_level
                    stockout_flag = 1

                restock = np.random.randint(8, 28)
                stock_level = stock_level - qty_sold + restock
                stock_level = max(stock_level, 0)

                records.append({
                    "date": date,
                    "store_id": store,
                    "item_id": item,
                    "category": item_category_map[item],
                    "price": round(price, 2),
                    "on_promo": promo_flag,
                    "discount_pct": discount_pct,
                    "qty_sold": qty_sold,
                    "stock_on_hand": stock_level,
                    "stockout_flag": stockout_flag,
                    "supplier_lead_time_days": lead_time_map[item],
                    "unit_cost": round(base_price[item] * 0.7, 2),
                    "holding_cost_rate": 0.18,
                    "ordering_cost": 500
                })

    df = pd.DataFrame(records)
    return df