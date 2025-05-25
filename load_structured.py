import pandas as pd
import duckdb
import os

# Paths
base_data_path = 'C:/Users/Shubh/Projects_VS/AllyIn/data/customers.csv'
orders_data_path = 'C:/Users/Shubh/Projects_VS/AllyIn/data/orders.csv'

# Load CSVs into DataFrames
customers_df = pd.read_csv(base_data_path)
orders_df = pd.read_csv(orders_data_path)

# Create DuckDB tables
duckdb.sql("CREATE TABLE customers AS SELECT * FROM customers_df")
duckdb.sql("CREATE TABLE orders AS SELECT * FROM orders_df")

# Create staging tables (normalized copies)
duckdb.sql("CREATE TABLE staging_customers AS SELECT * FROM customers")
duckdb.sql("CREATE TABLE staging_orders AS SELECT * FROM orders")

# Show customers table contents
print("Customers Table:")
print(duckdb.sql("SELECT * FROM customers").df())

# Show orders table contents
print("\nOrders Table:")
print(duckdb.sql("SELECT * FROM orders").df())

# Save tables to Parquet
duckdb.sql("COPY customers TO 'customers.parquet' (FORMAT PARQUET)")
duckdb.sql("COPY orders TO 'orders.parquet' (FORMAT PARQUET)")

# Save staging tables to CSV
duckdb.sql("COPY staging_customers TO 'staging_customers.csv' (HEADER, DELIMITER ',')")
duckdb.sql("COPY staging_orders TO 'staging_orders.csv' (HEADER, DELIMITER ',')")

print("\nTables saved successfully as Parquet and CSV files.")
