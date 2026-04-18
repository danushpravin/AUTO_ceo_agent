from world.generate_world import (
    WorldConfig,
    generate_range,
    simulate_next_day,
    write_outputs,
    write_unit_econ,
    generate_spend_inefficiency,
    flat_demand_profile,
)
from datetime import datetime, timedelta
import json
from pathlib import Path


def load_world_from_company(company_id: str) -> WorldConfig:
    path = Path("data/companies") / company_id / "config.json"
    with open(path, "r") as f:
        data = json.load(f)
    return WorldConfig(**data)


def build_world_from_user(form: dict, company_id: str = None) -> WorldConfig:
    """Convert user input form into a WorldConfig object or load from disk."""
    if not form:
        return load_world_from_company(company_id)

    return WorldConfig(
        PRODUCTS=form["products"],
        REGIONS=form["regions"],
        CHANNELS=form["channels"],
        UNIT_ECON=form["unit_econ"],
        BASE_DAILY_DEMAND=form["base_demand"],
        REGION_W=form["region_weights"],
        CHANNEL_W=form["channel_weights"],
        CHANNEL_BEHAVIOR=form["channel_behavior"],
        STARTING_STOCK=form["starting_stock"],
        PRODUCTION_RANGE=form["production_range"],
        DEMAND_NOISE=form["demand_noise"],
        DEMAND_PROFILE=form.get("demand_profile", {}),
    )


def create_company(company_id: str, form: dict, start_year: int = 2025):
    """
    Create a new company with one year of historical data.
    Data is deterministic per company_id.
    """
    config = build_world_from_user(form)

    # --- Auto-generate spend_inefficiency if not provided ---
    avg_price = sum(
        v["selling_price"] for v in config.UNIT_ECON.values()
    ) / len(config.UNIT_ECON)

    for channel in config.CHANNELS:
        if "spend_inefficiency" not in config.CHANNEL_BEHAVIOR[channel]:
            config.CHANNEL_BEHAVIOR[channel]["spend_inefficiency"] = (
                generate_spend_inefficiency(channel, avg_price)
            )

    # --- Fallback: flat demand profile for any product missing one ---
    for product in config.PRODUCTS:
        if product not in config.DEMAND_PROFILE:
            config.DEMAND_PROFILE[product] = flat_demand_profile()

    # --- Persist config ---
    path = Path("data/companies") / company_id / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(config.__dict__, f, indent=2)

    write_unit_econ(config, company_id)

    start_date = f"{start_year}-01-01"
    end_date = f"{start_year}-12-31"

    seed = hash(company_id) % (2**32)
    sales, marketing, inventory = generate_range(start_date, end_date, config, seed=seed)
    write_outputs(sales, marketing, inventory, company_id)

    print(f"✅ Company '{company_id}' created with one year of historical data ({start_year})")
    return config


def simulate_next_n_days(config: WorldConfig, company_id: str, n_days: int = 1, seed: int = None):
    """Simulate the next n business days for a company."""
    for _ in range(n_days):
        simulate_next_day(config, company_id, seed=seed)


def simulate_next_day_ui(company_id: str, form: dict, deterministic: bool = False):
    config = build_world_from_user(form, company_id)
    seed = hash(company_id) % (2**32) if deterministic else None
    simulate_next_day(config, company_id, seed=seed)