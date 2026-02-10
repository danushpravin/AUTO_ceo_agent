import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPANIES_ROOT = PROJECT_ROOT / "data" / "companies"
COMPANIES_ROOT.mkdir(exist_ok=True)


# =========================
# CONFIG (WORLD RULES)
# =========================
@dataclass
class WorldConfig:
    PRODUCTS: list
    REGIONS: list
    CHANNELS: list

    UNIT_ECON: dict
    BASE_DAILY_DEMAND: dict

    REGION_W: dict
    CHANNEL_W: dict
    CHANNEL_BEHAVIOR: dict

    STARTING_STOCK: int
    PRODUCTION_RANGE: dict
    DEMAND_NOISE: tuple

CSV_SCHEMAS = {
    "sales.csv": ["date","product","region","channel","units_sold","revenue","CAC"],
    "marketing.csv": ["date","channel","spend","impressions","clicks","conversions","revenue"],
    "inventory.csv": ["date","product","opening_stock","units_produced","units_dispatched","closing_stock","lost_demand","stockout_flag"],
    "unit_economics.csv": ["product","selling_price","cogs","gross_margin","packaging_cost","logistics_cost"],
}


# =========================
# HELPERS
# =========================

def _safe_int(x: float) -> int:
    return int(max(0, round(x)))

def _alloc(total: int, weights: dict, rng: np.random.Generator) -> dict:
    """Integer allocation of total across keys by weights."""
    keys = list(weights.keys())
    w = np.array([weights[k] for k in keys], dtype=float)
    w = w / w.sum()
    raw = rng.multinomial(total, w)
    return {k: int(v) for k, v in zip(keys, raw)}

def ensure_csv_schema(path: Path, columns: list):
    if not path.exists():
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)


def simulate_day(date: datetime, stock_state: dict, rng: np.random.Generator, config: WorldConfig):
    """
    Returns:
      sales_day_df, marketing_day_df, inventory_day_df, updated_stock_state
    """

    # 1) Demand (per product)
    product_demand = {}
    for p in config.PRODUCTS:
        noise = rng.uniform(*config.DEMAND_NOISE)
        product_demand[p] = _safe_int(config.BASE_DAILY_DEMAND[p] * noise)

    # 2) Inventory: produce first
    inventory_rows = []
    produced_today = {}
    for p in config.PRODUCTS:
        opening = stock_state.get(p, config.STARTING_STOCK)
        prod_lo, prod_hi = config.PRODUCTION_RANGE[p]
        produced = int(rng.integers(prod_lo, prod_hi + 1))
        if rng.random() < 0.18:  # 18% of days
            produced = int(produced * rng.uniform(0.0, 0.3))

        produced_today[p] = produced

        inventory_rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "product": p,
            "opening_stock": opening,
            "units_produced": produced,
            "units_dispatched": 0,   # fill after sales
            "closing_stock": opening + produced,  # temp, update later
            "lost_demand": 0,
            "stockout_flag": "No",
        })

    inventory_df = pd.DataFrame(inventory_rows)

    # 3) Sales allocation by region+channel, capped by inventory
    sales_rows = []
    for p in config.PRODUCTS:
        available = int(inventory_df.loc[inventory_df["product"] == p, "closing_stock"].iloc[0])
        demand = product_demand[p]
        actual_sold = min(demand, available)
        lost_demand = max(0, demand - available)

        # allocate across regions then channels
        region_alloc = _alloc(actual_sold, config.REGION_W, rng)
        for r, units_r in region_alloc.items():
            channel_alloc = _alloc(units_r, config.CHANNEL_W, rng)
            for c, units in channel_alloc.items():
                price = config.UNIT_ECON[p]["selling_price"]
                revenue = units * price
                sales_rows.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "product": p,
                    "region": r,
                    "channel": c,
                    "units_sold": units,
                    "revenue": revenue,
                    "CAC": None,  # fill after marketing computes CAC per channel
                })

        # update inventory dispatched + closing
        idx = inventory_df.index[inventory_df["product"] == p][0]
        inventory_df.at[idx, "units_dispatched"] = actual_sold
        closing = int(inventory_df.at[idx, "opening_stock"] + inventory_df.at[idx, "units_produced"] - actual_sold)
        inventory_df.at[idx, "closing_stock"] = closing
        inventory_df.at[idx, "lost_demand"] = lost_demand
        inventory_df.at[idx, "stockout_flag"] = "Yes" if closing <= 0 else "No"

        # update state
        stock_state[p] = closing

    sales_df = pd.DataFrame(sales_rows)

    # 4) Marketing (per channel) — revenue attributed from sales by channel
    marketing_rows = []
    revenue_by_channel = sales_df.groupby("channel")["revenue"].sum().to_dict()

    for c in config.CHANNELS:
        channel_rev = float(revenue_by_channel.get(c, 0.0))

        # spend derived from desired ROAS-ish behavior (but noisy)
        # Spend proportional to revenue capture, with channel inefficiency baked in
        # Google tends to burn more.
        ineff = {"Instagram": (0.18, 0.28), "Google": (0.30, 0.55), "Influencers": (0.28, 0.60)}[c]
        spend = channel_rev * rng.uniform(*ineff)
        spend = float(max(0.0, round(spend, 2)))

        beh = config.CHANNEL_BEHAVIOR[c]
        ctr = rng.uniform(*beh["ctr"])
        cvr = rng.uniform(*beh["cvr"])
        cpc = rng.uniform(*beh["cpc"])

        clicks = _safe_int(spend / cpc) if spend > 0 else 0
        impressions = _safe_int(clicks / ctr) if ctr > 0 else 0
        conversions = _safe_int(clicks * cvr)

        marketing_rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "channel": c,
            "spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": channel_rev,
        })

    marketing_df = pd.DataFrame(marketing_rows)

    # 5) CAC injection into sales rows (per channel-day CAC)
    cac_by_channel = {}
    for _, row in marketing_df.iterrows():
        conv = float(row["conversions"])
        spend = float(row["spend"])
        cac = (spend / conv) if conv > 0 else None
        cac_by_channel[row["channel"]] = cac

    sales_df["CAC"] = sales_df["channel"].map(cac_by_channel)

    return sales_df, marketing_df, inventory_df, stock_state

def write_unit_econ(config: WorldConfig, company_id: str):
    path = COMPANIES_ROOT / company_id
    path.mkdir(parents=True, exist_ok=True)

    econ_path = path / "unit_economics.csv"
    ensure_csv_schema(econ_path, CSV_SCHEMAS["unit_economics.csv"])

    rows = []
    for p in config.PRODUCTS:
        econ = config.UNIT_ECON[p]
        rows.append({
            "product": p,
            "selling_price": econ["selling_price"],
            "cogs": econ["cogs"],
            "gross_margin": econ["selling_price"] - econ["cogs"],
            "packaging_cost": econ["packaging_cost"],
            "logistics_cost": econ["logistics_cost"],
        })

    df = pd.DataFrame(rows)
    df.to_csv(path / "unit_economics.csv", index=False)



def generate_range(start_date: str, end_date: str, config: WorldConfig, seed: int = 42):
    """
    Generates inclusive date range data.
    """
    rng = np.random.default_rng(seed)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    stock_state = {p: config.STARTING_STOCK for p in config.PRODUCTS}

    all_sales = []
    all_marketing = []
    all_inventory = []

    cur = start
    while cur <= end:
        s, m, i, stock_state = simulate_day(cur, stock_state, rng, config)
        all_sales.append(s)
        all_marketing.append(m)
        all_inventory.append(i)
        cur += timedelta(days=1)

    return (
        pd.concat(all_sales, ignore_index=True),
        pd.concat(all_marketing, ignore_index=True),
        pd.concat(all_inventory, ignore_index=True),
    )


def write_outputs(sales_df, marketing_df, inventory_df, company_id):
    out = COMPANIES_ROOT / company_id
    out.mkdir(exist_ok=True, parents=True)

    sales_path = out / "sales.csv"
    marketing_path = out / "marketing.csv"
    inventory_path = out / "inventory.csv"

    ensure_csv_schema(sales_path, CSV_SCHEMAS["sales.csv"])
    ensure_csv_schema(marketing_path, CSV_SCHEMAS["marketing.csv"])
    ensure_csv_schema(inventory_path, CSV_SCHEMAS["inventory.csv"])

    sales_df.to_csv(sales_path, index=False)
    marketing_df.to_csv(marketing_path, index=False)
    inventory_df.to_csv(inventory_path, index=False)

    print("✅ Wrote:")
    print(f" - {sales_path} ({len(sales_df):,} rows)")
    print(f" - {marketing_path} ({len(marketing_df):,} rows)")
    print(f" - {inventory_path} ({len(inventory_df):,} rows)")
    
def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.exists() and path.stat().st_size > 0:
        return pd.read_csv(path)
    return pd.DataFrame()

def simulate_next_day(config: WorldConfig, company_id, seed=None):
    rng = np.random.default_rng(seed)

    data_dir = COMPANIES_ROOT / company_id

    sales_path = data_dir / "sales.csv"
    marketing_path = data_dir / "marketing.csv"
    inventory_path = data_dir / "inventory.csv"

    # --- Load existing data ---
    sales_df = read_csv_if_exists(sales_path)
    inventory_df = read_csv_if_exists(inventory_path)

    if sales_df.empty or inventory_df.empty:
        raise RuntimeError("❌ Cannot simulate next day without historical data.")

    # --- Determine last date ---
    sales_df["date"] = pd.to_datetime(sales_df["date"])
    inventory_df["date"] = pd.to_datetime(inventory_df["date"])

 


    last_date = sales_df["date"].max()
    next_date = last_date + timedelta(days=1)

    day_seed = (
        hash((seed, next_date.strftime("%Y-%m-%d"))) % (2**32)
        if seed is not None else None
    )

    rng = np.random.default_rng(day_seed)

    # --- Reconstruct stock state from last inventory snapshot ---
    
    last_inventory = (
        inventory_df.sort_values("date")
        .groupby("product")
        .tail(1)
    )

    stock_state = {
        row["product"]: int(row["closing_stock"])
        for _, row in last_inventory.iterrows()
    }

    # --- Simulate one day ---
    s, m, i, _ = simulate_day(next_date, stock_state, rng, config)

    # --- Append ---
    s.to_csv(sales_path, mode="a", header=False, index=False)
    m.to_csv(marketing_path, mode="a", header=False, index=False)
    i.to_csv(inventory_path, mode="a", header=False, index=False)

    print(f"✅ Simulated next business day: {next_date.date()}")




