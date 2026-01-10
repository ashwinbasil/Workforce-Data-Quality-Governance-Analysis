import pandas as pd

df = pd.read_csv("data/raw/uk_gov_workforce_raw.csv", encoding="latin1")

print("Shape:", df.shape)

print("\nColumns:")
for c in df.columns:
    print(c)

print("\nNull percentages:")
print((df.isnull().mean() * 100).round(2))

print("\nSample rows:")
print(df.head(10))
