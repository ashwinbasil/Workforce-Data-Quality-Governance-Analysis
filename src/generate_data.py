import pandas as pd
from faker import Faker
import random
from pathlib import Path

# Initialize Faker
fake = Faker()

# Number of records
N = 5000

# Resolve project root safely
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "raw"
OUTPUT_PATH = OUTPUT_DIR / "customers_raw.csv"

# Prepare data list
data = []

for i in range(N):
    customer_id = i + 1
    name = fake.name()

    # Introduce missing emails in ~5% of records
    email = fake.email() if random.random() > 0.05 else None

    # Introduce missing phone numbers in ~10% of records
    phone_number = fake.phone_number() if random.random() > 0.1 else None

    signup_date = fake.date_between(start_date="-3y", end_date="today")
    country = random.choice(["USA", "UK", "Canada", "Germany", "India"])
    last_active = fake.date_between(start_date=signup_date, end_date="today")

    data.append([
        customer_id,
        name,
        email,
        phone_number,
        signup_date,
        country,
        last_active
    ])

# Create DataFrame
df = pd.DataFrame(
    data,
    columns=[
        "customer_id",
        "name",
        "email",
        "phone_number",
        "signup_date",
        "country",
        "last_active"
    ]
)

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Save CSV
df.to_csv(OUTPUT_PATH, index=False)

print(f"Synthetic customer dataset created: {OUTPUT_PATH}")
