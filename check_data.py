import pandas as pd

df = pd.read_csv("data/retail_sales_data.csv")

print("Shape:", df.shape)
print("Stores:", df["store_id"].nunique())
print("Items:", df["item_id"].nunique())
print("Dates:", df["date"].nunique())