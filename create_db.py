# create_db.py

import sqlite3
import pandas as pd

conn = sqlite3.connect("shopit.db")

customers = pd.read_csv("DATA/customers.csv")
products = pd.read_csv("DATA/products.csv")
sales = pd.read_csv("DATA/sales_orders.csv")
product_performance= pd.read_csv("DATA/product_performance.csv")
customer_summary= pd.read_csv("DATA/customer_summary.csv")
customers.to_sql(
    "customers",
    conn,
    if_exists="replace",
    index=False
)

products.to_sql(
    "products",
    conn,
    if_exists="replace",
    index=False
)

sales.to_sql(
    "sales_orders",
    conn,
    if_exists="replace",
    index=False
)
product_performance.to_sql(
    "product_performance",
    conn,
    if_exists="replace",
    index=False
)
customer_summary.to_sql(
    "customer_summary",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print("Database Created Successfully")