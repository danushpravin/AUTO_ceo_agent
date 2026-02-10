import pandas as pd
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
# ------------------------------------------------------
# Helper: load all datasets so functions can access them
# ------------------------------------------------------

REQUIRED = {
  "sales": ["date","product","region","channel","units_sold","revenue","CAC"],
  "marketing": ["date","channel","spend","impressions","clicks","conversions","revenue"],
  "inventory": ["date","product","opening_stock","units_produced","units_dispatched","closing_stock","lost_demand","stockout_flag"],
  "unit_economics": ["product","selling_price","cogs","packaging_cost","logistics_cost"],
}

@dataclass
class DataContext:
    sales: pd.DataFrame
    marketing: pd.DataFrame
    inventory: pd.DataFrame
    unit: pd.DataFrame
    sales_enriched: pd.DataFrame  # sales + unit costs columns
    daily: pd.DataFrame          # daily totals (fast baseline queries)

def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)

def _validate(df: pd.DataFrame, name: str):
    missing = [c for c in REQUIRED[name] if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing columns: {missing}")

def load_context(company_id: str,base_dir="data/companies") -> DataContext:
    data_dir = Path(base_dir) / company_id

    if not data_dir.exists():
        raise ValueError(f"Company '{company_id}' not found at {data_dir}")

    sales = _read_csv(data_dir / "sales.csv")
    marketing = _read_csv(data_dir / "marketing.csv")
    inventory = _read_csv(data_dir / "inventory.csv")
    unit = _read_csv(data_dir / "unit_economics.csv")

    for name, df in {
        "sales": sales,
        "marketing": marketing,
        "inventory": inventory,
        "unit": unit
    }.items():
        if df.empty:
            raise ValueError(f"{name}.csv is empty for company {company_id}")


    _validate(sales, "sales")
    _validate(marketing, "marketing")
    _validate(inventory, "inventory")
    _validate(unit, "unit_economics")

    # Parse dates ONCE
    sales["date"] = pd.to_datetime(sales["date"])
    marketing["date"] = pd.to_datetime(marketing["date"])
    inventory["date"] = pd.to_datetime(inventory["date"])

    # Enrich sales with unit costs ONCE (avoid repeated merges)
    unit = unit.copy()
    unit["unit_cost"] = unit["cogs"] + unit["packaging_cost"] + unit["logistics_cost"]
    sales_enriched = sales.merge(unit[["product", "unit_cost"]], on="product", how="left")

    # Daily totals table (fast baseline + anomalies)
    daily = (sales.groupby("date", as_index=False)
                  .agg(revenue=("revenue","sum"),
                       units=("units_sold","sum")))

    return DataContext(
        sales=sales, marketing=marketing, inventory=inventory, unit=unit,
        sales_enriched=sales_enriched, daily=daily
    )


