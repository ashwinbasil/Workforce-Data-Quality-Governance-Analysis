import pandas as pd

# Load the generated CSV
df = pd.read_csv('../data/raw/customers_raw.csv')

# Show first 5 rows
print("First 5 rows of dataset:")
print(df.head())

# Show missing values per column
print("\nMissing values per column:")
print(df.isna().sum())
