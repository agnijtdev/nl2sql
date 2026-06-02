"""
Run this once to create a sample database to test your app.
python databases/create_sample_db.py
"""

import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("databases/sample.db")
c = conn.cursor()

# Create tables
c.executescript("""
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE,
    city        TEXT,
    joined_date TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    category TEXT,
    price    REAL,
    stock    INTEGER
);

CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    product_id  INTEGER REFERENCES products(id),
    quantity    INTEGER,
    order_date  TEXT,
    status      TEXT
);
""")

# Seed data
cities    = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kochi"]
categories= ["Electronics", "Clothing", "Books", "Food", "Sports"]
statuses  = ["pending", "shipped", "delivered", "cancelled"]

for i in range(1, 51):
    c.execute(
        "INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?)",
        (i, f"Customer {i}", f"user{i}@example.com",
         random.choice(cities),
         (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")),
    )

for i in range(1, 21):
    c.execute(
        "INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)",
        (i, f"Product {i}", random.choice(categories),
         round(random.uniform(10, 500), 2), random.randint(0, 200)),
    )

for i in range(1, 201):
    c.execute(
        "INSERT OR IGNORE INTO orders VALUES (?,?,?,?,?,?)",
        (i, random.randint(1, 50), random.randint(1, 20),
         random.randint(1, 5),
         (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
         random.choice(statuses)),
    )

conn.commit()
conn.close()
print("✅ Sample database created at databases/sample.db")