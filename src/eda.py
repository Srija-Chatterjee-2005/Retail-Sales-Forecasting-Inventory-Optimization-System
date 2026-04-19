import os
import matplotlib.pyplot as plt
import pandas as pd

def generate_eda_outputs(df):
    os.makedirs("images", exist_ok=True)

    # Daily sales trend
    daily_sales = df.groupby("date", as_index=False)["qty_sold"].sum()
    plt.figure(figsize=(12, 5))
    plt.plot(daily_sales["date"], daily_sales["qty_sold"])
    plt.title("Daily Retail Sales Trend")
    plt.xlabel("Date")
    plt.ylabel("Units Sold")
    plt.tight_layout()
    plt.savefig("images/daily_sales_trend.png")
    plt.close()

    # Category-wise sales
    category_sales = df.groupby("category", as_index=False)["qty_sold"].sum()
    plt.figure(figsize=(8, 5))
    plt.bar(category_sales["category"], category_sales["qty_sold"])
    plt.title("Category-wise Sales")
    plt.xlabel("Category")
    plt.ylabel("Total Units Sold")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig("images/category_sales.png")
    plt.close()

    # Promo vs non-promo
    promo_sales = df.groupby("on_promo", as_index=False)["qty_sold"].mean()
    plt.figure(figsize=(6, 4))
    plt.bar(promo_sales["on_promo"].astype(str), promo_sales["qty_sold"])
    plt.title("Average Sales: Promo vs Non-Promo")
    plt.xlabel("On Promo")
    plt.ylabel("Average Qty Sold")
    plt.tight_layout()
    plt.savefig("images/promo_vs_nonpromo.png")
    plt.close()