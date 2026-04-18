import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field


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

    # Optional — auto-generated at company creation if not provided
    # Structure per product:
    # {
    #   "seasonality": [12 floats, one per month],
    #   "trend": {"type": "growth"|"decay"|"stable", "start": float, "peak_month": int, "end": float},
    #   "events": [{"name": str, "date": "MM-DD", "duration_days": int, "multiplier": float}]
    # }
    DEMAND_PROFILE: dict = field(default_factory=dict)


CSV_SCHEMAS = {
    "sales.csv": ["date", "product", "region", "channel", "units_sold", "revenue", "CAC"],
    "marketing.csv": ["date", "channel", "spend", "impressions", "clicks", "conversions", "revenue"],
    "inventory.csv": ["date", "product", "opening_stock", "units_produced", "units_dispatched", "closing_stock", "lost_demand", "stockout_flag"],
    "unit_economics.csv": ["product", "selling_price", "cogs", "gross_margin", "packaging_cost", "logistics_cost"],
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


def generate_spend_inefficiency(channel: str, selling_price_avg: float) -> list:
    """
    Derives spend inefficiency range per channel based on
    channel type and average product price point.
    Higher price = harder conversion = more spend per revenue unit.
    """
    price_factor = min(1.5, max(0.8, selling_price_avg / 1000))

    base = {
        "Instagram":  [0.18, 0.30],
        "Google":     [0.22, 0.40],
        "Influencers": [0.28, 0.55],
    }.get(channel, [0.20, 0.40])

    return [round(base[0] * price_factor, 3), round(base[1] * price_factor, 3)]


def flat_demand_profile() -> dict:
    """
    Fallback profile — no seasonality, no trend, no events.
    Used when LLM generation fails.
    """
    return {
        "seasonality": [1.0] * 12,
        "trend": {"type": "stable", "start": 1.0, "peak_month": 6, "end": 1.0},
        "events": [],
    }


def get_demand_multiplier(product: str, date: datetime, config: WorldConfig) -> float:
    """
    Combines seasonality + trend + event spike into a single demand multiplier.
    Falls back to 1.0 if no profile exists for the product.
    """
    profile = config.DEMAND_PROFILE.get(product)
    if not profile:
        return 1.0

    # --- Seasonality ---
    month_idx = date.month - 1
    seasonality = profile.get("seasonality", [1.0] * 12)
    seasonal_mult = seasonality[month_idx]

    # --- Trend ---
    trend = profile.get("trend", {"type": "stable", "start": 1.0, "peak_month": 6, "end": 1.0})
    m = date.month
    peak = trend.get("peak_month", 6)
    t_type = trend.get("type", "stable")
    t_start = trend.get("start", 1.0)
    t_end = trend.get("end", 1.0)

    if t_type == "stable":
        trend_mult = 1.0

    elif t_type == "growth":
        # Ramp from start → 1.0 by peak_month, then hold at end
        if m <= peak:
            trend_mult = t_start + (1.0 - t_start) * (m - 1) / max(peak - 1, 1)
        else:
            trend_mult = 1.0 + (t_end - 1.0) * (m - peak) / max(12 - peak, 1)

    elif t_type == "decay":
        # Linear decay from start → end over the year
        trend_mult = t_start - (t_start - t_end) * (m - 1) / 11

    else:
        trend_mult = 1.0

    # --- Events ---
    event_mult = 1.0
    for event in profile.get("events", []):
        try:
            e_month, e_day = map(int, event["date"].split("-"))
            e_start = datetime(date.year, e_month, e_day)
            e_end = e_start + timedelta(days=event.get("duration_days", 1))
            if e_start <= date < e_end:
                event_mult = max(event_mult, event.get("multiplier", 1.0))
        except (ValueError, KeyError):
            continue

    return seasonal_mult * trend_mult * event_mult


def ensure_csv_schema(path: Path, columns: list):
    if not path.exists():
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)


def simulate_day(date: datetime, stock_state: dict, rng: np.random.Generator, config: WorldConfig):
    """
    Returns:
      sales_day_df, marketing_day_df, inventory_day_df, updated_stock_state
    """

    # 1) Demand (per product) — now includes seasonality + trend + events
    product_demand = {}
    for p in config.PRODUCTS:
        noise = rng.uniform(*config.DEMAND_NOISE)
        demand_mult = get_demand_multiplier(p, date, config)
        product_demand[p] = _safe_int(config.BASE_DAILY_DEMAND[p] * demand_mult * noise)

    # 2) Inventory: produce first
    inventory_rows = []
    produced_today = {}
    for p in config.PRODUCTS:
        opening = stock_state.get(p, config.STARTING_STOCK)
        prod_lo, prod_hi = config.PRODUCTION_RANGE[p]
        produced = int(rng.integers(prod_lo, prod_hi + 1))
        if rng.random() < 0.06:  # 6% of days — realistic supply disruption
            produced = int(produced * rng.uniform(0.4, 0.7))

        produced_today[p] = produced

        inventory_rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "product": p,
            "opening_stock": opening,
            "units_produced": produced,
            "units_dispatched": 0,
            "closing_stock": opening + produced,  # temp, updated after sales
            "lost_demand": 0,
            "stockout_flag": "No",
        })

    inventory_df = pd.DataFrame(inventory_rows)

    # 3) Sales allocation by region + channel, capped by inventory
    sales_rows = []
    for p in config.PRODUCTS:
        available = int(inventory_df.loc[inventory_df["product"] == p, "closing_stock"].iloc[0])
        demand = product_demand[p]
        actual_sold = min(demand, available)
        lost_demand = max(0, demand - available)

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
                    "CAC": None,
                })

        idx = inventory_df.index[inventory_df["product"] == p][0]
        inventory_df.at[idx, "units_dispatched"] = actual_sold
        closing = int(
            inventory_df.at[idx, "opening_stock"]
            + inventory_df.at[idx, "units_produced"]
            - actual_sold
        )
        inventory_df.at[idx, "closing_stock"] = closing
        inventory_df.at[idx, "lost_demand"] = lost_demand
        inventory_df.at[idx, "stockout_flag"] = "Yes" if lost_demand > 0 else "No"

        stock_state[p] = closing

    sales_df = pd.DataFrame(sales_rows)

    # 4) Marketing (per channel)
    marketing_rows = []
    revenue_by_channel = sales_df.groupby("channel")["revenue"].sum().to_dict()

    for c in config.CHANNELS:
        channel_rev = float(revenue_by_channel.get(c, 0.0))

        beh = config.CHANNEL_BEHAVIOR[c]
        ineff = beh.get("spend_inefficiency", [0.20, 0.35])
        spend = channel_rev * rng.uniform(*ineff)
        spend = float(max(0.0, round(spend, 2)))

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

    # 5) CAC injection into sales rows
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
    """Generates inclusive date range data."""
    rng = np.random.default_rng(seed)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    stock_state = {p: config.STARTING_STOCK for p in config.PRODUCTS}

    all_sales, all_marketing, all_inventory = [], [], []

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
    print(f"  - {sales_path} ({len(sales_df):,} rows)")
    print(f"  - {marketing_path} ({len(marketing_df):,} rows)")
    print(f"  - {inventory_path} ({len(inventory_df):,} rows)")


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if path.exists() and path.stat().st_size > 0:
        return pd.read_csv(path)
    return pd.DataFrame()


def simulate_next_day(config: WorldConfig, company_id, seed=None):
    data_dir = COMPANIES_ROOT / company_id

    sales_path = data_dir / "sales.csv"
    marketing_path = data_dir / "marketing.csv"
    inventory_path = data_dir / "inventory.csv"

    sales_df = read_csv_if_exists(sales_path)
    inventory_df = read_csv_if_exists(inventory_path)

    if sales_df.empty or inventory_df.empty:
        raise RuntimeError("❌ Cannot simulate next day without historical data.")

    sales_df["date"] = pd.to_datetime(sales_df["date"])
    inventory_df["date"] = pd.to_datetime(inventory_df["date"])

    last_date = sales_df["date"].max()
    next_date = last_date + timedelta(days=1)

    day_seed = (
        hash((seed, next_date.strftime("%Y-%m-%d"))) % (2**32)
        if seed is not None else None
    )

    rng = np.random.default_rng(day_seed)

    last_inventory = (
        inventory_df.sort_values("date")
        .groupby("product")
        .tail(1)
    )

    stock_state = {
        row["product"]: int(row["closing_stock"])
        for _, row in last_inventory.iterrows()
    }

    s, m, i, _ = simulate_day(next_date, stock_state, rng, config)

    s.to_csv(sales_path, mode="a", header=False, index=False)
    m.to_csv(marketing_path, mode="a", header=False, index=False)
    i.to_csv(inventory_path, mode="a", header=False, index=False)

    print(f"✅ Simulated next business day: {next_date.date()}")