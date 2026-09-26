"""
generate_synthetic.py
Creates sales_agent.db with realistic FMCG synthetic data.
Schema mirrors the SFA system (same field names and relationships).

Run:
    pip install faker
    python data/generate_synthetic.py
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_agent.db")

# ─── SCHEMA ──────────────────────────────────────────────────────────────────

TABLES = [
    """CREATE TABLE IF NOT EXISTS M_DISTRIBUTOR (
        DIST_CD     TEXT PRIMARY KEY,
        DIST_NAME   TEXT NOT NULL,
        COUNTRY_CD  TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS MST_PRDCAT (
        PRDCAT2_CD  TEXT PRIMARY KEY,
        PRDCAT_DESC TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS MST_PRD (
        PRD_CD      TEXT PRIMARY KEY,
        PRD_DESC    TEXT NOT NULL,
        PRDCAT2_CD  TEXT NOT NULL,
        UNIT_PRICE  REAL NOT NULL,
        UOM         TEXT NOT NULL,
        FOREIGN KEY (PRDCAT2_CD) REFERENCES MST_PRDCAT(PRDCAT2_CD))""",
    """CREATE TABLE IF NOT EXISTS M_SALESMAN (
        SALESMAN_CD   TEXT PRIMARY KEY,
        DIST_CD       TEXT NOT NULL,
        SALESMAN_NAME TEXT NOT NULL,
        SALESMAN_TYPE TEXT NOT NULL,
        FOREIGN KEY (DIST_CD) REFERENCES M_DISTRIBUTOR(DIST_CD))""",
    """CREATE TABLE IF NOT EXISTS M_CUST (
        CUST_CD         TEXT PRIMARY KEY,
        DIST_CD         TEXT NOT NULL,
        CUST_NAME       TEXT NOT NULL,
        CUST_TYPE       TEXT NOT NULL,
        CUST_HIER3      TEXT NOT NULL,
        OUTSTANDING_BAL REAL NOT NULL DEFAULT 0,
        CUST_CRDLMT     REAL NOT NULL DEFAULT 10000,
        ADDR_1          TEXT,
        ADDR_2          TEXT,
        ADDR_3          TEXT,
        ADDR_4          TEXT,
        ADDR_5          TEXT,
        ADDR_POSTAL     TEXT,
        LATITUDE        REAL,
        LONGITUDE       REAL,
        FOREIGN KEY (DIST_CD) REFERENCES M_DISTRIBUTOR(DIST_CD))""",
    """CREATE TABLE IF NOT EXISTS M_INVENTORY (
        DIST_CD     TEXT NOT NULL,
        PRD_CD      TEXT NOT NULL,
        QTY_ON_HAND REAL NOT NULL DEFAULT 0,
        UOM         TEXT NOT NULL,
        PRIMARY KEY (DIST_CD, PRD_CD),
        FOREIGN KEY (DIST_CD) REFERENCES M_DISTRIBUTOR(DIST_CD),
        FOREIGN KEY (PRD_CD)  REFERENCES MST_PRD(PRD_CD))""",
    """CREATE TABLE IF NOT EXISTS MST_ROUTECUST (
        DIST_CD     TEXT NOT NULL,
        SALESMAN_CD TEXT NOT NULL,
        CYCLE_CD    TEXT NOT NULL,
        CUST_CD     TEXT NOT NULL,
        START_DT    TEXT NOT NULL,
        END_DT      TEXT,
        PRIMARY KEY (DIST_CD, SALESMAN_CD, CUST_CD),
        FOREIGN KEY (DIST_CD)     REFERENCES M_DISTRIBUTOR(DIST_CD),
        FOREIGN KEY (SALESMAN_CD) REFERENCES M_SALESMAN(SALESMAN_CD),
        FOREIGN KEY (CUST_CD)     REFERENCES M_CUST(CUST_CD))""",
    """CREATE TABLE IF NOT EXISTS M_ROUTEPLAN (
        DIST_CD     TEXT NOT NULL,
        SALESMAN_CD TEXT NOT NULL,
        CUST_CD     TEXT NOT NULL,
        VISIT_DT    TEXT NOT NULL,
        FOREIGN KEY (DIST_CD)     REFERENCES M_DISTRIBUTOR(DIST_CD),
        FOREIGN KEY (SALESMAN_CD) REFERENCES M_SALESMAN(SALESMAN_CD),
        FOREIGN KEY (CUST_CD)     REFERENCES M_CUST(CUST_CD))""",
    """CREATE TABLE IF NOT EXISTS RPT_DAYSLSHISTDTL (
        DIST_CD      TEXT NOT NULL,
        CUST_CD      TEXT NOT NULL,
        PRD_CD       TEXT NOT NULL,
        PRDCAT2_CD   TEXT NOT NULL,
        VISIT_DT     TEXT NOT NULL,
        INV_QTY_SML  REAL NOT NULL DEFAULT 0,
        INV_AMT      REAL NOT NULL DEFAULT 0,
        INV_DISC_AMT REAL NOT NULL DEFAULT 0,
        INV_FOC_AMT  REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (DIST_CD) REFERENCES M_DISTRIBUTOR(DIST_CD),
        FOREIGN KEY (CUST_CD) REFERENCES M_CUST(CUST_CD),
        FOREIGN KEY (PRD_CD)  REFERENCES MST_PRD(PRD_CD))""",
    """CREATE TABLE IF NOT EXISTS M_PRFMHDR_CUST (
        DIST_CD   TEXT    NOT NULL,
        CUST_CD   TEXT    NOT NULL,
        CAL_YEAR  INTEGER NOT NULL,
        CAL_MTH   INTEGER NOT NULL,
        SALES_AMT REAL    NOT NULL DEFAULT 0,
        PRIMARY KEY (DIST_CD, CUST_CD, CAL_YEAR, CAL_MTH),
        FOREIGN KEY (DIST_CD) REFERENCES M_DISTRIBUTOR(DIST_CD),
        FOREIGN KEY (CUST_CD) REFERENCES M_CUST(CUST_CD))""",
    """CREATE TABLE IF NOT EXISTS M_MTHCUST (
        CUST_CD TEXT PRIMARY KEY,
        AMS     REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (CUST_CD) REFERENCES M_CUST(CUST_CD))"""
]

# ─── REFERENCE DATA ───────────────────────────────────────────────────────────

DISTRIBUTORS = [
    ("D001", "Alpha Distribution Sdn Bhd", "MY"),
    ("D002", "Beta Trading Pte Ltd",        "SG"),
    ("D003", "Gamma Supplies Co",           "ID"),
]

CATEGORIES = [
    ("CAT-BEV", "Beverages"),
    ("CAT-DAI", "Dairy"),
    ("CAT-CON", "Confectionery"),
    ("CAT-CUL", "Culinary"),
]

PRODUCTS = [
    ("PRD-001", "Beverage Powder 2kg",    "CAT-BEV", 3750.00, "EA"),
    ("PRD-002", "Beverage Powder 500g",   "CAT-BEV", 1050.00, "EA"),
    ("PRD-003", "Instant Drink Mix 1kg",  "CAT-BEV", 2300.00, "EA"),
    ("PRD-004", "Fruit Drink Sachet 30s", "CAT-BEV",  650.00, "EA"),
    ("PRD-005", "Creamer Powder 1kg",     "CAT-DAI", 1850.00, "EA"),
    ("PRD-006", "Full Cream Milk 1L",     "CAT-DAI", 1550.00, "EA"),
    ("PRD-007", "Condensed Milk 500g",    "CAT-DAI", 1150.00, "EA"),
    ("PRD-008", "Low Fat Milk 1L",        "CAT-DAI", 1600.00, "EA"),
    ("PRD-009", "Chocolate Bar 50g",      "CAT-CON",  290.00, "EA"),
    ("PRD-010", "Wafer Biscuit 150g",     "CAT-CON",  420.00, "EA"),
    ("PRD-011", "Chocolate Box 200g",     "CAT-CON", 1350.00, "EA"),
    ("PRD-012", "Candy Assorted 200g",    "CAT-CON",  580.00, "EA"),
    ("PRD-013", "Seasoning Powder 500g",  "CAT-CUL",  920.00, "EA"),
    ("PRD-014", "Cooking Cream 250ml",    "CAT-CUL", 1100.00, "EA"),
    ("PRD-015", "Instant Noodle 5pk",     "CAT-CUL",  750.00, "EA"),
    ("PRD-016", "Tomato Sauce 340g",      "CAT-CUL",  699.00, "EA"),
    ("PRD-017", "Cereal Box 500g",        "CAT-BEV", 1999.00, "EA"),
    ("PRD-018", "Oat Drink 1L",           "CAT-DAI", 1699.00, "EA"),
    ("PRD-019", "Premium Coffee 250g",    "CAT-BEV", 2900.00, "EA"),
    ("PRD-020", "Cocoa Powder 500g",      "CAT-BEV", 1500.00, "EA"),
]

CUST_TYPES   = ["Retailer", "Wholesaler", "Minimarket", "Supermarket"]
HIER3_VALUES = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def months_back(n):
    today = datetime.today()
    month = today.month - n
    year  = today.year
    while month <= 0:
        month += 12
        year  -= 1
    return datetime(year, month, 1)

def fmt(dt):
    return dt.strftime("%Y-%m-%d")

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def generate():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur  = conn.cursor()

    for stmt in TABLES:
        cur.execute(stmt)
    conn.commit()

    # 1. Distributors
    cur.executemany("INSERT INTO M_DISTRIBUTOR VALUES (?,?,?)", DISTRIBUTORS)
    print(f"✓ M_DISTRIBUTOR      — {len(DISTRIBUTORS)} records")

    # 2. Product categories
    cur.executemany("INSERT INTO MST_PRDCAT VALUES (?,?)", CATEGORIES)
    print(f"✓ MST_PRDCAT         — {len(CATEGORIES)} records")

    # 3. Products
    cur.executemany("INSERT INTO MST_PRD VALUES (?,?,?,?,?)", PRODUCTS)
    print(f"✓ MST_PRD            — {len(PRODUCTS)} records")

    # 4. Salesmen
    dist_codes = [d[0] for d in DISTRIBUTORS]
    salesmen = [
        (f"SM{i:03d}", dist_codes[i % len(dist_codes)], fake.name(), random.choice(["O","T"]))
        for i in range(1, 11)
    ]
    cur.executemany("INSERT INTO M_SALESMAN VALUES (?,?,?,?)", salesmen)
    print(f"✓ M_SALESMAN         — {len(salesmen)} records")

    # 5. Customers (with embedded scenarios)
    #    CT0000000001–0005 → churn risk   (no orders last 40+ days)
    #    CT0000000006–0008 → credit risk  (outstanding > 85% of limit)
    #    CT0000000009–0013 → dropout      (no orders last 3 months)
    customers = []
    for i in range(1, 101):
        cust_cd      = f"CT{i:010d}"
        credit_limit = random.choice([5000, 10000, 20000, 30000, 50000])
        outstanding  = round(
            credit_limit * random.uniform(0.85, 0.98) if i in range(6, 9)
            else credit_limit * random.uniform(0.05, 0.60), 2
        )
        customers.append((
            cust_cd, dist_codes[i % len(dist_codes)],
            fake.company(), random.choice(CUST_TYPES), random.choice(HIER3_VALUES),
            outstanding, credit_limit,
            fake.street_address(), fake.city(), fake.state(), "", "", fake.postcode(),
            round(random.uniform(2.0, 7.0), 6),
            round(random.uniform(100.0, 120.0), 6),
        ))
    cur.executemany("INSERT INTO M_CUST VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", customers)
    print(f"✓ M_CUST             — {len(customers)} records")

    # 6. Inventory
    inventory = []
    for dist_cd, *_ in DISTRIBUTORS:
        for prd_cd, _, _, _, uom in PRODUCTS:
            qty = random.randint(0, 10) if random.random() < 0.15 else random.randint(50, 500)
            inventory.append((dist_cd, prd_cd, qty, uom))
    cur.executemany("INSERT INTO M_INVENTORY VALUES (?,?,?,?)", inventory)
    print(f"✓ M_INVENTORY        — {len(inventory)} records")

    # 7. Route assignment + 8. Route plan
    sm_codes    = [s[0] for s in salesmen]
    today       = datetime.today()
    route_assign, route_plan = [], []

    for idx, (cust_cd, dist_cd, *_) in enumerate(customers):
        sm_cd  = sm_codes[idx % len(sm_codes)]
        cycle  = random.choice(["WK", "FN"])
        route_assign.append((dist_cd, sm_cd, f"CYC-{cycle}", cust_cd, fmt(months_back(12)), None))
        visit_dt = today + timedelta(days=random.randint(1, 7))
        for _ in range(4):
            route_plan.append((dist_cd, sm_cd, cust_cd, fmt(visit_dt)))
            visit_dt += timedelta(days=7 if cycle == "WK" else 14)

    cur.executemany("INSERT OR IGNORE INTO MST_ROUTECUST VALUES (?,?,?,?,?,?)", route_assign)
    cur.executemany("INSERT INTO M_ROUTEPLAN VALUES (?,?,?,?)", route_plan)
    print(f"✓ MST_ROUTECUST      — {len(route_assign)} records")
    print(f"✓ M_ROUTEPLAN        — {len(route_plan)} records")

    # 9. Sales history
    prd_price = {p[0]: p[3] for p in PRODUCTS}
    prd_cat   = {p[0]: p[2] for p in PRODUCTS}
    prd_codes = [p[0] for p in PRODUCTS]

    cust_products = {
        cust_cd: {prd: random.randint(5, 40) for prd in random.sample(prd_codes, random.randint(3, 8))}
        for cust_cd, *_ in customers
    }

    history_rows, monthly_totals = [], {}

    for cust_cd, dist_cd, *_ in customers:
        cust_idx = int(cust_cd[-4:])
        for m in range(12, 0, -1):
            order_dt     = months_back(m)
            year, month  = order_dt.year, order_dt.month

            if cust_idx <= 5 and m <= 2:        continue  # churn scenario
            if 9 <= cust_idx <= 13 and m <= 3:  continue  # dropout scenario
            if random.random() < 0.10:           continue  # natural skip

            visit_dt      = order_dt.replace(day=random.randint(1, 28))
            monthly_sales = 0.0

            for prd_cd, base_qty in cust_products[cust_cd].items():
                seasonal = 1.3 if month in [11, 12] else 1.0
                qty  = max(1, round(base_qty * random.uniform(0.8, 1.2) * seasonal))
                amt  = round(qty * prd_price[prd_cd], 4)
                disc = round(amt * random.uniform(0.00, 0.05), 4)
                foc  = round(amt * random.uniform(0.00, 0.02), 4)
                history_rows.append((dist_cd, cust_cd, prd_cd, prd_cat[prd_cd], fmt(visit_dt), qty, amt, disc, foc))
                monthly_sales += amt

            key = (dist_cd, cust_cd, year, month)
            monthly_totals[key] = monthly_totals.get(key, 0) + monthly_sales

    cur.executemany("INSERT INTO RPT_DAYSLSHISTDTL VALUES (?,?,?,?,?,?,?,?,?)", history_rows)
    print(f"✓ RPT_DAYSLSHISTDTL  — {len(history_rows)} records")

    # 10. Monthly performance aggregates
    perf_rows = [(d, c, y, m, round(a, 2)) for (d, c, y, m), a in monthly_totals.items()]
    cur.executemany("INSERT INTO M_PRFMHDR_CUST VALUES (?,?,?,?,?)", perf_rows)
    print(f"✓ M_PRFMHDR_CUST     — {len(perf_rows)} records")

    # 11. Average monthly sales per customer
    cust_total  = {}
    cust_months = {}
    for (_, cust_cd, _, _), amt in monthly_totals.items():
        cust_total[cust_cd]  = cust_total.get(cust_cd, 0) + amt
        cust_months[cust_cd] = cust_months.get(cust_cd, 0) + 1

    ams_rows = [(c, round(cust_total[c] / cust_months[c], 2)) for c in cust_total]
    cur.executemany("INSERT INTO M_MTHCUST VALUES (?,?)", ams_rows)
    print(f"✓ M_MTHCUST          — {len(ams_rows)} records")

    conn.commit()
    conn.close()
    print(f"\n✅ Database ready → {DB_PATH}")

if __name__ == "__main__":
    generate()