# tools.py
from typing import Dict, Any
import pandas as pd

from agent.core.context import load_context
from agent.analytics.sales import (
    sales_by_product,
    sales_by_region,
    sales_by_channel,
    revenue_by_month,
    top_products,
    top_regions,
)

from agent.analytics.inventory import (
    stockouts_by_product,
    avg_closing_stock,
)

from agent.analytics.marketing import (
    roas_by_channel,
    spend_over_time,
)

from agent.analytics.profit import (
    profit_by_product,
    true_profit_by_channel,
    cost_components_by_product,
)

from agent.analytics.executive import (
    daily_delta,
    revenue_recent_performance,
)

from agent.reasoning.interpret import (
    interpret_growth_quality,
    marketing_efficiency,
    product_portfolio_health,
    inventory_health_vs_revenue,
    channel_dependency_risk,
)

from agent.decisions.recommend import generate_recommendations

# Load ONCE
CTX = None
CURRENT_COMPANY = None

def init_company(company_id: str):
    global CTX, CURRENT_COMPANY
    CTX = load_context(company_id)
    CURRENT_COMPANY = company_id

# ----------------------
# EXECUTIVE TOOLS
# ----------------------

def tool_daily_delta() -> Dict[str, Any]:
    return daily_delta(CTX)

def tool_revenue_recent_performance(n: int = 7) -> Dict[str, Any]:
    return revenue_recent_performance(CTX, n=n)

def tool_top_products(n: int = 3):
    return top_products(CTX, n=n).to_dict("records")

def tool_top_regions(n: int = 3):
    return top_regions(CTX, n=n).to_dict("records")

def tool_true_profit_by_channel():
    return true_profit_by_channel(CTX).to_dict("records")


# ----------------------
# ANALYTICS TOOLS
# ----------------------

def tool_sales_by_product():
    return sales_by_product(CTX).to_dict("records")

def tool_sales_by_region():
    return sales_by_region(CTX).to_dict("records")

def tool_sales_by_channel():
    return sales_by_channel(CTX).to_dict("records")

def tool_revenue_by_month():
    return revenue_by_month(CTX).to_dict("records")

def tool_profit_by_product():
    return profit_by_product(CTX).to_dict("records")

def tool_cost_components_by_product():
    return cost_components_by_product(CTX).to_dict("records")

# ------------------------------
# INVENTORY TOOLS
# ------------------------------

def tool_inventory_stockouts():
    return stockouts_by_product(CTX).to_dict("records")

def tool_inventory_avg_stock():
    return avg_closing_stock(CTX).to_dict("records")

# ------------------------------
# MARKETING TOOLS
# ------------------------------

def tool_marketing_roas():
    return roas_by_channel(CTX).to_dict(orient = "records")

def tool_marketing_spend_trend():
    return spend_over_time(CTX).to_dict(orient = "records")

# ----------------------
# INTERPRETATION TOOLS 
# ----------------------

def tool_interpret_growth_quality():
    recent = revenue_recent_performance(CTX, n=7)
    prof = profit_by_product(CTX)
    return interpret_growth_quality(recent, prof)

def tool_marketing_efficiency(lookback_days: int = 30):
    return marketing_efficiency(CTX,lookback_days=lookback_days)

def tool_product_portfolio_health():
    return product_portfolio_health(CTX)

def tool_inventory_health_vs_revenue(lookback_days: int = 30):
    return inventory_health_vs_revenue(CTX, lookback_days=lookback_days)

def tool_channel_dependency_risk():
    return channel_dependency_risk(CTX)

# ----------------------
# RECOMMENDATION TOOL
# ----------------------

def tool_generate_recommendations():
    """
    Central executive recommendation primitive.
    Aggregates all interpretation flags + growth signal.
    """

    flags = []

    # Collect flags from all interpretation primitives
    me = marketing_efficiency(CTX)
    pp = product_portfolio_health(CTX)
    inv = inventory_health_vs_revenue(CTX)
    ch = channel_dependency_risk(CTX)

    for block in [me, pp, inv, ch]:
        flags.extend(block.get("flags", []))

    # Growth quality is signal-based, not flag-based
    growth_signal = interpret_growth_quality(
        revenue_recent_performance(CTX, n=7),
        profit_by_product(CTX)
    )

    return generate_recommendations(
        flags=flags,
        growth_signal=growth_signal
    )

