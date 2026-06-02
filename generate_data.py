"""
Generate a realistic synthetic general ledger with planted anomalies.
All data is fabricated. No real entity, vendor, or transaction is represented.
Designed so the detection engine has real signals to find.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

rng = np.random.default_rng(42)
random.seed(42)

# --- Reference data ---------------------------------------------------------
VENDORS = [
    "Apex Office Supply", "Brightline Logistics", "Cedar Tech Solutions",
    "Delphi Consulting Grp", "Evergreen Facilities", "Forge Industrial",
    "Granite Legal LLP", "Harbor Freight Co", "Ironwood Marketing",
    "Juniper Software Inc", "Kestrel Travel", "Lumen Utilities",
    "Meridian Staffing", "Northstar Insurance", "Onyx Maintenance",
    "Pinnacle Catering", "Quartz Printing", "Redwood Security Svcs",
    "Summit Equipment", "Titan Telecom",
]
ACCOUNTS = {
    "5010": "Office Supplies", "5020": "Professional Fees",
    "5030": "Travel & Entertainment", "5040": "IT & Software",
    "5050": "Facilities & Rent", "5060": "Marketing",
    "5070": "Utilities", "5080": "Equipment", "5090": "Misc Expense",
}
USERS = ["jchen", "mpatel", "rgomez", "klee", "twright", "afarah"]
APPROVAL_LIMIT = 5000  # entries just under this are suspicious

rows = []
start = datetime(2025, 1, 1)

def workday_amount(base_lo, base_hi):
    # Realistic non-round amounts: dollars + cents, Benford-friendly distribution
    mant = rng.uniform(1, 10)
    scale = 10 ** rng.integers(1, 4)
    val = mant * scale
    val = max(base_lo, min(base_hi, val))
    return round(val, 2)

# --- Clean baseline population (~1500 entries) ------------------------------
for i in range(1500):
    day_offset = int(rng.integers(0, 365))
    date = start + timedelta(days=day_offset)
    # mostly weekdays
    while date.weekday() >= 5 and rng.random() < 0.92:
        date = start + timedelta(days=int(rng.integers(0, 365)))
    acct = random.choice(list(ACCOUNTS.keys()))
    rows.append({
        "entry_id": 100000 + i,
        "date": date.strftime("%Y-%m-%d"),
        "post_time": f"{int(rng.integers(8,18)):02d}:{int(rng.integers(0,60)):02d}",
        "account": acct,
        "account_name": ACCOUNTS[acct],
        "vendor": random.choice(VENDORS),
        "description": "Standard operating expense",
        "amount": workday_amount(50, 9000),
        "user": random.choice(USERS),
    })

next_id = 100000 + 1500

# --- Planted anomaly 1: duplicate payments ----------------------------------
for _ in range(8):
    src = random.choice(rows)
    dup = src.copy()
    dup["entry_id"] = next_id; next_id += 1
    dup["description"] = "Standard operating expense"
    # same vendor, same amount, within a few days
    d = datetime.strptime(src["date"], "%Y-%m-%d") + timedelta(days=int(rng.integers(1,4)))
    dup["date"] = d.strftime("%Y-%m-%d")
    rows.append(dup)

# --- Planted anomaly 2: round-dollar entries --------------------------------
for _ in range(22):
    date = start + timedelta(days=int(rng.integers(0, 365)))
    acct = random.choice(list(ACCOUNTS.keys()))
    rows.append({
        "entry_id": next_id, "date": date.strftime("%Y-%m-%d"),
        "post_time": f"{int(rng.integers(8,18)):02d}:{int(rng.integers(0,60)):02d}",
        "account": acct, "account_name": ACCOUNTS[acct],
        "vendor": random.choice(VENDORS), "description": "Adjusting entry",
        "amount": float(rng.choice([1000, 2000, 2500, 5000, 10000, 15000])),
        "user": random.choice(USERS),
    }); next_id += 1

# --- Planted anomaly 3: just-under-threshold clustering ---------------------
for _ in range(15):
    date = start + timedelta(days=int(rng.integers(0, 365)))
    rows.append({
        "entry_id": next_id, "date": date.strftime("%Y-%m-%d"),
        "post_time": f"{int(rng.integers(8,18)):02d}:{int(rng.integers(0,60)):02d}",
        "account": "5020", "account_name": ACCOUNTS["5020"],
        "vendor": "Delphi Consulting Grp", "description": "Consulting services",
        "amount": round(float(rng.uniform(4750, 4999)), 2),
        "user": "twright",
    }); next_id += 1

# --- Planted anomaly 4: weekend / after-hours postings ----------------------
for _ in range(12):
    # force a weekend date
    date = start + timedelta(days=int(rng.integers(0, 365)))
    while date.weekday() < 5:
        date += timedelta(days=1)
    rows.append({
        "entry_id": next_id, "date": date.strftime("%Y-%m-%d"),
        "post_time": f"{int(rng.integers(0,5)):02d}:{int(rng.integers(0,60)):02d}",
        "account": random.choice(list(ACCOUNTS.keys())),
        "account_name": "Misc Expense",
        "vendor": random.choice(VENDORS), "description": "Late posting",
        "amount": workday_amount(500, 8000), "user": "afarah",
    }); next_id += 1

# --- Planted anomaly 5: vendor outliers (Benford-violating large spikes) ----
for _ in range(6):
    date = start + timedelta(days=int(rng.integers(0, 365)))
    rows.append({
        "entry_id": next_id, "date": date.strftime("%Y-%m-%d"),
        "post_time": f"{int(rng.integers(8,18)):02d}:{int(rng.integers(0,60)):02d}",
        "account": "5090", "account_name": ACCOUNTS["5090"],
        "vendor": "Ironwood Marketing", "description": "Special project",
        "amount": round(float(rng.uniform(45000, 90000)), 2),
        "user": "afarah",
    }); next_id += 1

df = pd.DataFrame(rows)
df = df.sample(frac=1, random_state=1).reset_index(drop=True)  # shuffle
df.to_csv("/home/claude/ledgerlens/sample_ledger.csv", index=False)
print(f"Generated {len(df)} entries")
print(df.head(10).to_string())
print("\nAmount stats:")
print(df["amount"].describe())
